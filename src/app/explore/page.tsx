import type { Metadata } from "next";import { Suspense } from "react";import ExplorerShell from "@/features/explorer/ExplorerShell";import "./explore.css";
export const metadata:Metadata={title:"Explore 2025 | Melbourne Urban Pulse",description:"Explore Melbourne pedestrian Pulses across twelve representative sensors."};
export default function ExplorePage(){return <Suspense fallback={<main className="explorer-loading">Loading Annual Explorer…</main>}><ExplorerShell/></Suspense>}
