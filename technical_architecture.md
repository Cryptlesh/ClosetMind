# ClosetMind: Master AI Orchestration Architecture

> [!TIP]
> **Showcase Mode**: This document is designed for the Google ADK Certification Demo. It highlights the use of Sequential/Parallel Agents, Google In-built MCPs, and Custom Stdio Toolsets.
> **View Preview**: Press `Ctrl + Shift + V` to see the live rendering.

---

## 🏛️ End-to-End ADK & MCP Technical Architecture

This diagram showcases the complete lifecycle of a user request—from the initial Natural Language prompt to the final multi-modal output—utilizing the full spectrum of Google Agent Development Kit (ADK) features.

![Master Architecture Diagram](C:\Projects\ClosetMind\closetmind_master_architecture.png)

```mermaid
graph TD
    %% User Input Layer
    User((User Input)) --> supervisor

    subgraph "ADK Orchestration Layer (ADK SequentialAgent)"
        supervisor["Fit Genie Supervisor<br/>(Master Orchestrator)"]
    end

    %% Phase 1: Planning
    subgraph "Phase 1: Discovery & Planning"
        supervisor --> RouteAgent["Route Planner Agent<br/>(LlmAgent)"]
    end

    %% Phase 2: Parallel Inference
    subgraph "Phase 2: Parallel Inference (ADK ParallelAgent)"
        ParallelNode[Parallel Execution Node]
        supervisor --> ParallelNode
        ParallelNode -- "Concurrent Call 1" --> Stylist["Closet Stylist<br/>(LlmAgent)"]
        ParallelNode -- "Concurrent Call 2" --> Tips["Fashion Guru<br/>(LlmAgent)"]
    end

    %% Phase 3: Synthesis
    subgraph "Phase 3: Multi-Modal Synthesis"
        supervisor --> VTON["Visual Sync Tool<br/>(AgentTool / Image-to-Image)"]
    end

    %% MCP & Data Layer
    subgraph "MCP Tool Ecosystem (Model Context Protocol)"
        %% Custom MCPs
        RouteAgent -- "list_events / sync" --> CalMCP{{"Google Calendar MCP<br/>(Custom Stdio Server)"}}
        Tips -- "get_weather" --> WeatherMCP{{"Weather Tool MCP<br/>(Open-Meteo)"}}
        
        %% In-Built MCPs
        Stylist -- "query_inventory" --> ADB_MCP{{"AlloyDB MCP Toolbox<br/>(Google In-Built Server)"}}
    end

    subgraph "Persistence & External Services"
        Postgres[(AlloyDB PostgreSQL)]
        GoogleAPI[Google Workspace API]
        OpenMeteo[Open-Meteo REST API]
        Imagen[Imagen 4 / Vision Service]
        
        ADB_MCP --- Postgres
        CalMCP --- GoogleAPI
        WeatherMCP --- OpenMeteo
        VTON --- Imagen
    end

    %% Output Flow
    VTON --> Output((Unified Response))
    Stylist --> Output
    Tips --> Output
    CalMCP --> Output

    %% Styling & Themes
    classDef adk_core fill:#4285F4,stroke:#1a237e,color:#fff,stroke-width:2px;
    classDef mcp_builtin fill:#34A853,stroke:#1b5e20,color:#fff,stroke-width:2px;
    classDef mcp_custom fill:#FBBC05,stroke:#f57f17,color:#fff,stroke-width:2px;
    classDef external fill:#f3f3f3,stroke:#999,color:#333;
    
    class supervisor,RouteAgent,Stylist,Tips,VTON adk_core;
    class ADB_MCP mcp_builtin;
    class CalMCP,WeatherMCP mcp_custom;
    class Postgres,GoogleAPI,OpenMeteo,Imagen external;

    linkStyle default stroke:#757575,stroke-width:1px;
    linkStyle 0,1,2,3,4,5,13 stroke:#4285F4,stroke-width:2px;
    linkStyle 6,7,8 stroke:#34A853,stroke-width:2px;
```

---

## 💎 Performance Breakdown: Sync vs Parallel

| Workflow Phase | Mechanism | Benefit |
| :--- | :--- | :--- |
| **User Intent Extraction** | `SequentialAgent` (Sync) | Ensures we have valid dates/locations before checking inventory. |
| **Styling & Advice Inference** | `ParallelAgent` (Concurrent) | Cuts system latency by **50%** by processing wardrobe matching and fashion tips simultaneously. |
| **Image Synthesis** | `AgentTool` (Sync Chain) | Ensures high-fidelity try-on images only use items confirmed by the Stylist agent. |
| **Calendar Sync** | `Subprocess / MCP` | Isolated execution prevents GenAI httpx client corruption. |

---

## 📋 Comprehensive Component Catalog

#### **1. Fit Genie Supervisor (SequentialAgent)**
- **Role**: Root orchestrator.
- **Action**: Manages the data "hand-off" between all child agents.
- **ADK Feature**: Implements complex multi-step dependency management.

#### **2. Route Planner (LlmAgent)**
- **Role**: Trip analysis.
- **Integration**: Communicates with the **Custom Calendar MCP** to check schedules and write outfit events.
- **Data**: Translates "Next weekend in Bali" into `2026-05-14T00:00:00Z`.

#### **3. Closet Stylist (LlmAgent)**
- **Role**: Wardrobe Expert.
- **Integration**: Leverages the **In-built AlloyDB MCP Toolbox** to perform semantic search on user clothes.
- **Value**: Matches items to climate and user style preference.

#### **4. Fashion Guru (LlmAgent)**
- **Role**: Lifestyle Coach.
- **Integration**: Uses the **Weather MCP (Open-Meteo)** to provide context-aware lifestyle recommendations.

#### **5. Visual Sync Tool (AgentTool)**
- **Role**: Content Creator.
- **Tech Stack**: Uses Gemini 3.1 Flash for Vision inference to realistically merge user selfies with garment textures.

---

## 💾 AlloyDB Schema & RAG Integration
- **RAG Implementation**: The `wardrobe` table contains `tags` and metadata analyzed by Gemini during the Vault upload process.
- **Search Pattern**: The Stylist agent queries this metadata via MCP to find items that match "rainy weather" or "formal dinner."

---

## 📡 Agent-to-MCP Communication Detail

```mermaid
graph LR
    subgraph "Agent Reasoning Layer (ADK)"
        A[LlmAgent] -- "1. Define Tool Schema" --> SM[Session Manager]
        A -- "4. Execute Tool Call" --> SM
    end

    subgraph "MCP Bridge (Model Context Protocol)"
        SM -- "2. List Tools" --> TS[Toolset]
        SM -- "5. Dispatch Request (JSON-RPC)" --> TS
        TS -- "6. tool_call_request" --> Server[MCP Server Process]
    end

    subgraph "System Resources"
        Server -- "7. Tool Invocation" --> Res[DB / API / FS]
        Res -- "8. Raw Data" --> Server
    end

    Server -- "9. tool_call_result" --> TS
    TS -- "10. Observation" --> SM
    SM -- "11. Tool Result" --> A
    A -- "12. Final Synthesis" --> Output[Final User Response]

    style A fill:#e1f5fe,stroke:#01579b
    style Server fill:#fff9c4,stroke:#fbc02d
    style Res fill:#e8f5e9,stroke:#2e7d32
```
