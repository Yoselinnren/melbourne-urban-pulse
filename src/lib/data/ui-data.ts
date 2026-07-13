import type { AnnualOverviewData, PulseDetailData, PulseId, PulseIndexItem, SensorDetailData, SensorId, SensorIndexItem, UiManifest } from "@/lib/types/ui-data";

export class UiDataError extends Error { constructor(message:string, public payload:string){super(message)} }
export type PulseIndexData={schemaVersion:string;dataVersion:string;sensorMode:string;items:PulseIndexItem[]};
export type SensorIndexData={schemaVersion:string;dataVersion:string;sensorMode:string;items:SensorIndexItem[]};
export type InitialUiData={manifest:UiManifest;annual:AnnualOverviewData;pulses:PulseIndexData;sensors:SensorIndexData};
const pulseCache=new Map<PulseId,Promise<PulseDetailData>>(), sensorCache=new Map<SensorId,Promise<SensorDetailData>>();
async function get<T>(url:string,label:string,signal?:AbortSignal):Promise<T>{const r=await fetch(url,{signal});if(!r.ok)throw new UiDataError(`${label} request failed (${r.status})`,label);try{return await r.json() as T}catch{throw new UiDataError(`${label} is not valid JSON`,label)}}
const object=(v:unknown):v is Record<string,unknown>=>typeof v==="object"&&v!==null;
export async function loadInitialData(signal?:AbortSignal):Promise<InitialUiData>{
  const [manifest,annual,sensors,pulses]=await Promise.all([get<UiManifest>("/data/ui/v1/manifest.json","manifest",signal),get<AnnualOverviewData>("/data/ui/v1/annual-overview.json","annual overview",signal),get<SensorIndexData>("/data/ui/v1/sensors/index.json","sensor index",signal),get<PulseIndexData>("/data/ui/v1/pulses/index.json","pulse index",signal)]);
  if(!object(manifest)||!object(annual)||!object(sensors)||!object(pulses)||!Array.isArray(sensors.items)||!Array.isArray(pulses.items))throw new UiDataError("A UI payload has an invalid top-level structure.","initial data");
  const version=manifest.dataVersion;
  if(!version||[annual,sensors,pulses].some(x=>x.dataVersion!==version))throw new UiDataError("UI data files are out of sync. Regenerate or redeploy the UI dataset.","data version");
  if(sensors.items.length!==12||pulses.items.length!==425||sensors.items.some(x=>!x.sensorId)||pulses.items.some(x=>!x.pulseId))throw new UiDataError("UI indexes have unexpected counts or canonical IDs.","indexes");
  return {manifest,annual,sensors,pulses};
}
export function loadPulseDetail(id:PulseId){if(!pulseCache.has(id))pulseCache.set(id,get<PulseDetailData>(`/data/ui/v1/pulses/${encodeURIComponent(id)}.json`,"Pulse detail"));return pulseCache.get(id)!}
export function loadSensorDetail(id:SensorId){if(!sensorCache.has(id))sensorCache.set(id,get<SensorDetailData>(`/data/ui/v1/sensors/${encodeURIComponent(id)}.json`,"Sensor detail"));return sensorCache.get(id)!}
export function clearPulseCache(id:PulseId){pulseCache.delete(id)} export function clearSensorCache(id:SensorId){sensorCache.delete(id)}
