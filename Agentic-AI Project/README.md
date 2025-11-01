
# Agenti-AI Project: Autonomous Web Interaction Agent

## Document Version: 1.0

***

## 1. Executive Summary

The **Agenti-AI Project** is an autonomous web interaction agent built on n8n that controls a remote browser to perform user-defined tasks. The system transforms natural language commands into automated browser operations through a sophisticated agentic workflow, enabling complex web automation without manual intervention.

**Core Value:** Automates repetitive web tasks like data extraction, navigation, and interaction that typically require human effort.

## 2. Real-World Problem & Solution

**Problem:** Competitive Price Monitoring
- Manual price tracking across e-commerce sites is time-consuming and error-prone
- Businesses need automated, reliable competitor monitoring
- Human-based web interaction doesn't scale for multiple products/sites

**Agentic Solution:**
- **User Command:** "Find MacBook Pro prices on bestbuy.com"
- **Agent Execution:** 
  - Launches browser session
  - Navigates to target website
  - Searches for specified products
  - Extracts and returns pricing data
- **Output:** Structured data ready for analysis or database storage

## 3. System Architecture

### 3.1. Architecture Overview

```
User Input → Chat Trigger → Browser Agent → Tool Selection → External APIs → Results
     |              |              |              |               |           |
     |              |              |              |               |           |
  Slack     Memory Buffer    Language Model    Airtop Tools   OpenRouter   User Output
  Notification   |           (Gemini 2.0)     (Click/Type/    (LLM Service)
                 |                             Query/Load)
           Conversation History
```



### 3.2. Core Components

**Agent Layer:**
- Browser Agent Node: Central decision-making engine
- Language Model: Google Gemini 2.0 Flash via OpenRouter
- Memory System: Buffer window for conversation history

**Tool Layer:**
- Browser Control: Start_Browser, Load URL, Click, Type, Query, End Session
- Reasoning: Think tool for planning and reflection
- Notification: Slack integration for live monitoring

**Infrastructure Layer:**
- n8n Workflow Engine: Orchestration platform
- Airtop.ai: Remote browser automation service
- OpenRouter: LLM API gateway

## 4. Technical Implementation

### 4.1. Workflow Execution Flow

<img width="1299" height="534" alt="Project Workflow" src="https://github.com/user-attachments/assets/3599df10-1e8f-4c71-99ed-ca7c406852f0" />


```
1. TRIGGER PHASE
   User Message → Chat Webhook → Agent Invocation

2. REASONING LOOP
   While (task_not_complete AND under_max_iterations):
     - Agent consults LLM with context and available tools
     - LLM returns tool selection and parameters
     - Agent executes selected tool via n8n
     - Tool interacts with Airtop browser API
     - Results fed back to agent for next decision

3. COMPLETION PHASE
   - End Session tool called for cleanup
   - Slack notification sent with results
   - Final response returned to user
```

### 4.2. Tool Specifications

**Start_Browser Tool**
- Purpose: Initialize browser session
- Parameters: profileName, timeoutMinutes
- Output: sessionId, windowId (required for all subsequent tools)

**Navigation Tools**
- Load URL: Direct browser to specific webpage
- Parameters: sessionId, windowId, url
- Use Case: Initial page loading and site navigation

**Interaction Tools**
- Click Tool: Simulate mouse clicks on web elements
- Parameters: sessionId, windowId, elementDescription
- Element Description: Detailed text description of target element

- Type Tool: Enter text into input fields
- Parameters: sessionId, windowId, text, elementDescription
- Auto-action: Presses Enter after typing

**Information Tools**
- Query Tool: Extract content and structure from current page
- Parameters: sessionId, windowId, prompt
- Function: Agent's "eyes" for understanding page state

**Management Tools**
- Think Tool: Internal reasoning without external action
- End Session: Cleanup and resource release

### 4.3. Data Flow Mechanism

**Dynamic Parameter Binding:**
- Uses `$fromAI()` expressions for runtime parameter injection
- Example: `$fromAI('Session_ID', "The sessionId from Start_Browser", 'string')`
- Enables agent to provide context-aware parameters for each tool call

**Memory Management:**
- Conversation history maintained in MemoryBufferWindow
- Enables multi-turn interactions and context preservation
- Configurable window size for history retention

## 5. Agentic Patterns & Design Principles

### 5.1. Implemented Patterns

**Tool-Using Agent Pattern**
- Agent has defined toolset with specific capabilities
- Learns to combine tools sequentially for task completion
- Each tool represents a discrete browser interaction capability

**Reasoning Loop Pattern**
- Continuous cycle: Observe → Think → Act
- Managed by n8n's Agent node with configurable max iterations
- Includes reflection via Think tool for complex decisions

**Handoff Pattern**
- Start_Browser tool delegates to specialized sub-workflow
- Separation of concerns for complex initialization logic
- Enables workflow reuse and maintenance

### 5.2. Safety & Guardrails

**Explicit Tool Boundaries**
- Agent restricted to predefined toolset only
- No arbitrary code execution capability
- All actions must go through approved tools

**Resource Management**
- Mandatory session cleanup via End Session tool
- Timeout configurations for long-running tasks
- Profile-based browser isolation

**Operational Guardrails**
- System prompt enforces step-by-step thinking
- Required tool sequences (Start_Browser first)
- Maximum iteration limits to prevent infinite loops

## 6. Deployment Configuration

### 6.1. Platform Requirements

**n8n Environment**
- n8n instance (cloud or self-hosted)
- Webhook configuration for chat interface
- Credential management for external services

**External Service Integrations**
- Airtop.ai account for browser automation
- OpenRouter API key for LLM access
- Slack webhook for notifications (optional)

### 6.2. Credential Setup

**Airtop Configuration**
- API key generation from airtop.ai
- Browser profile setup for target websites
- Session timeout and resource settings

**OpenRouter Setup**
- Account creation and API key generation
- Model selection (Gemini 2.0 Flash)
- Usage monitoring and cost control

## 7. Performance Characteristics

**Execution Scope**
- Single-session task completion
- Short to medium complexity web interactions
- Real-time operation with live browser feedback

**Scalability Considerations**
- Parallel execution possible with multiple n8n workers
- Browser session isolation enables concurrent tasks
- Memory window size configurable based on task complexity

## 8. Future Enhancement Pathways

**Advanced Memory Systems**
- Vector database integration for long-term memory
- Embedding-based similarity search for past solutions
- Persistent conversation history across sessions

**Multi-Agent Architecture**
- Specialist agents for different task types
- Supervisor agent for complex workflow coordination
- Inter-agent communication protocols

**Enhanced Tool Ecosystem**
- File download and processing capabilities
- Screenshot analysis with vision models
- Form filling and submission automation

**Production Monitoring**
- Performance metrics and logging
- Error handling and recovery mechanisms
- Usage analytics and optimization insights



## 9. Conclusion

The Agenti-AI Project demonstrates a production-ready implementation of agentic AI principles for web automation. By combining n8n's workflow orchestration with modern LLM capabilities and browser automation services, it creates a robust system for transforming natural language commands into automated web interactions. The architecture provides a solid foundation for extending into more complex multi-agent systems and enterprise-scale automation solutions.

