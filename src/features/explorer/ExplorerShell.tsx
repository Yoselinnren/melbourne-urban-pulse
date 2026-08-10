"use client";

import {useCallback,useEffect,useMemo,useReducer,useRef,useState} from "react";
import Link from "next/link";
import {usePathname,useRouter,useSearchParams} from "next/navigation";
import type {PulseDetailData,SensorDetailData} from "@/lib/types/ui-data";
import {clearPulseCache,clearSensorCache,loadInitialData,loadPulseDetail,loadSensorDetail,type InitialUiData} from "@/lib/data/ui-data";
import {initialState,reducer,type ExplorerState} from "./explorer-state";
import {canonicalizeUrl,toQuery,type UrlState} from "./explorer-url";
import ExplorerHeader from "./ExplorerHeader";
import ExplorerFilters from "./ExplorerFilters";
import SpatialCanvas from "./SpatialCanvas";
import TemporalRibbon from "./TemporalRibbon";
import ContextInspector from "./ContextInspector";
import ExplorerStatus from "./ExplorerStatus";

const syncError="UI data files are out of sync. Regenerate or redeploy the UI dataset.";

export default function ExplorerShell(){
  const router=useRouter(),pathname=usePathname(),params=useSearchParams();
  const [state,dispatch]=useReducer(reducer,initialState);
  const [data,setData]=useState<InitialUiData|null>(null);
  const [initialError,setInitialError]=useState<string|null>(null);
  const [pulseDetail,setPulseDetail]=useState<PulseDetailData|null>(null);
  const [sensorDetail,setSensorDetail]=useState<SensorDetailData|null>(null);
  const [pulseError,setPulseError]=useState<string|null>(null);
  const [sensorError,setSensorError]=useState<string|null>(null);
  const [retry,setRetry]=useState(0);
  const pulseRequest=useRef(0),sensorRequest=useRef(0);

  useEffect(()=>{const controller=new AbortController();loadInitialData(controller.signal).then(x=>{setData(x);dispatch({type:"status",key:"initialDataStatus",value:"ready"})}).catch(e=>{if(e?.name!=="AbortError"){setInitialError(e instanceof Error?e.message:"Initial data failed");dispatch({type:"status",key:"initialDataStatus",value:"error"})}});return()=>controller.abort()},[retry]);
  useEffect(()=>{if(!data)return;const canonical=canonicalizeUrl(new URLSearchParams(params.toString()),new Set(data.pulses.items.map(x=>x.pulseId)),new Set(data.sensors.items.map(x=>x.sensorId)));dispatch({type:"sync",value:{...canonical.value,notice:canonical.notice}});if(canonical.query!==params.toString())router.replace(`${pathname}${canonical.query?`?${canonical.query}`:""}`,{scroll:false})},[data,params,pathname,router]);

  const navigate=useCallback((next:Partial<ExplorerState>,clear=false)=>{const value:UrlState={month:next.month===undefined?state.month:next.month,direction:next.direction===undefined?state.direction:next.direction,scopes:next.scopes??state.scopes,evidenceReadiness:next.evidenceReadiness??state.evidenceReadiness,selectedPulseId:clear?null:(next.selectedPulseId===undefined?state.selectedPulseId:next.selectedPulseId),selectedSensorId:clear?null:(next.selectedSensorId===undefined?state.selectedSensorId:next.selectedSensorId)};const q=toQuery(value);router.push(`${pathname}${q?`?${q}`:""}`,{scroll:false})},[state,router,pathname]);
  const commitFilters=(next:Partial<ExplorerState>)=>navigate(next,true);

  const requestPulse=useCallback((id:string,retryFailed=false)=>{const request=++pulseRequest.current,current=()=>new URLSearchParams(window.location.search).get("pulse")===id;if(retryFailed)clearPulseCache(id);queueMicrotask(()=>{if(request===pulseRequest.current&&current()){setPulseError(null);setPulseDetail(null);dispatch({type:"status",key:"pulseDetailStatus",value:"loading"})}});return loadPulseDetail(id).then(x=>{if(request!==pulseRequest.current||!current())return;if(data&&x.dataVersion!==data.manifest.dataVersion)throw new Error(syncError);setPulseDetail(x);dispatch({type:"status",key:"pulseDetailStatus",value:"ready"})}).catch(e=>{if(request===pulseRequest.current&&current()){setPulseError(e instanceof Error?e.message:"Pulse detail payload could not be loaded.");dispatch({type:"status",key:"pulseDetailStatus",value:"error"})}})},[data]);
  const requestSensor=useCallback((id:string,retryFailed=false)=>{const request=++sensorRequest.current,current=()=>new URLSearchParams(window.location.search).get("sensor")===id;if(retryFailed)clearSensorCache(id);queueMicrotask(()=>{if(request===sensorRequest.current&&current()){setSensorError(null);setSensorDetail(null);dispatch({type:"status",key:"sensorDetailStatus",value:"loading"})}});return loadSensorDetail(id).then(x=>{if(request!==sensorRequest.current||!current())return;if(data&&x.dataVersion!==data.manifest.dataVersion)throw new Error(syncError);setSensorDetail(x);dispatch({type:"status",key:"sensorDetailStatus",value:"ready"})}).catch(e=>{if(request===sensorRequest.current&&current()){setSensorError(e instanceof Error?e.message:"Sensor detail payload could not be loaded.");dispatch({type:"status",key:"sensorDetailStatus",value:"error"})}})},[data]);
  useEffect(()=>{if(state.selectedPulseId){void requestPulse(state.selectedPulseId)}else{pulseRequest.current++}},[state.selectedPulseId,requestPulse]);
  useEffect(()=>{if(state.selectedSensorId){void requestSensor(state.selectedSensorId)}else{sensorRequest.current++}},[state.selectedSensorId,requestSensor]);

  const filtered=useMemo(()=>data?.pulses.items.filter(p=>(!state.month||p.month===state.month)&&(!state.direction||p.direction===state.direction)&&(!state.scopes.length||state.scopes.includes(p.scope))&&(!state.evidenceReadiness.length||state.evidenceReadiness.includes(p.evidenceReadiness)))??[],[data,state.month,state.direction,state.scopes,state.evidenceReadiness]);
  const pulse=data?.pulses.items.find(x=>x.pulseId===state.selectedPulseId)??null;
  const sensor=data?.sensors.items.find(x=>x.sensorId===state.selectedSensorId)??null;
  const preview=data?.pulses.items.find(x=>x.pulseId===(state.hoveredPulseId??state.selectedPulseId))??null;

  const retryPulse=()=>{if(state.selectedPulseId)void requestPulse(state.selectedPulseId,true)};
  const retrySensor=()=>{if(state.selectedSensorId)void requestSensor(state.selectedSensorId,true)};
  const currentContext=pulse?new Intl.DateTimeFormat("en-AU",{dateStyle:"medium",timeStyle:"short"}).format(new Date(pulse.start)):"Annual overview";

  return <div className="explorer-app">
    <ExplorerHeader state={state} count={filtered.length} currentContext={currentContext} onFilters={()=>dispatch({type:"set",key:"filtersOpen",value:!state.filtersOpen})} onClear={()=>navigate({selectedPulseId:null,selectedSensorId:null})} onReset={()=>navigate({month:null,direction:null,scopes:[],evidenceReadiness:[]},true)}/>
    <ExplorerFilters state={state} commit={commitFilters}/>
    <div className="sr-live" aria-live="polite">{state.notice??`${filtered.length} Pulses match current filters.`}</div>
    {state.initialDataStatus==="loading"&&<main className="explorer-stage skeleton-stage" aria-label="Loading Annual Explorer"><div className="upper"><div className="skeleton-block"><ExplorerStatus>Loading spatial data…</ExplorerStatus></div><div className="skeleton-block"><ExplorerStatus>Loading annual summary…</ExplorerStatus></div></div><div className="skeleton-block"><ExplorerStatus>Loading Pulse timeline…</ExplorerStatus></div></main>}
    {state.initialDataStatus==="error"&&<main className="explorer-stage loading-stage"><ExplorerStatus kind="error" onRetry={()=>{setInitialError(null);dispatch({type:"status",key:"initialDataStatus",value:"loading"});setRetry(x=>x+1)}}>{initialError}.</ExplorerStatus><Link href="/projects/melbourne-urban-pulse">Return to Project</Link></main>}
    {data&&state.initialDataStatus==="ready"&&<main className="explorer-stage"><div className="upper"><SpatialCanvas sensors={data.sensors.items} pulses={filtered} selectedPulse={preview} selectedSensor={state.selectedSensorId} hoveredSensor={state.hoveredSensorId} onHover={id=>dispatch({type:"set",key:"hoveredSensorId",value:id})} onSelect={id=>navigate({selectedSensorId:id})}/><ContextInspector annual={data.annual} filtered={filtered} filters={state} pulse={pulse} sensor={sensor} pulseDetail={pulseDetail} sensorDetail={sensorDetail} pulseStatus={state.pulseDetailStatus} sensorStatus={state.sensorDetailStatus} pulseError={pulseError} sensorError={sensorError} onCloseSensor={()=>navigate({selectedSensorId:null})} onRetryPulse={retryPulse} onRetrySensor={retrySensor}/></div><TemporalRibbon pulses={filtered} selected={state.selectedPulseId} hovered={state.hoveredPulseId} onHover={id=>dispatch({type:"set",key:"hoveredPulseId",value:id})} onSelect={id=>navigate({selectedPulseId:id,selectedSensorId:null})}/></main>}
  </div>;
}
