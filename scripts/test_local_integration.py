"""Script de prueba de integración local.

Verifica que el stack (Nexus + Fitness + Nutrition) esté funcionando
y que la orquestación A2A ocurra correctamente.
"""

import asyncio
import sys
import httpx
import json
from rich.console import Console
from rich.panel import Panel

console = Console()

NEXUS_URL = "http://localhost:8080"
FITNESS_URL = "http://localhost:8081"
NUTRITION_URL = "http://localhost:8082"

async def check_health(client: httpx.AsyncClient, name: str, url: str) -> bool:
    """Verifica healthz endpoint."""
    try:
        resp = await client.get(f"{url}/healthz")
        if resp.status_code == 200:
            console.print(f"[green]✔ {name} is healthy ({url})[/green]")
            return True
        else:
            console.print(f"[red]✘ {name} returned {resp.status_code}[/red]")
            return False
    except Exception as e:
        console.print(f"[red]✘ {name} is unreachable: {str(e)}[/red]")
        return False

async def test_orchestration(client: httpx.AsyncClient, message: str, expected_agent: str):
    """Prueba orquestación enviando mensaje a Nexus."""
    console.print(f"\n[bold blue]Testing Intent: '{message}'[/bold blue]")
    
    try:
        # Nexus espera { "message": ... } en /invoke (RPC style)
        # Pero main.py usa A2A payload structure? 
        # Revisando agents/nexus/main.py: handle_method recibe params.
        # A2AServer espera:
        # { "jsonrpc": "2.0", "method": "orchestrate", "params": { "message": "..." }, "id": 1 }
        
        payload = {
            "jsonrpc": "2.0",
            "method": "orchestrate",
            "params": {
                "message": message,
                "user_id": "test-user",
                "conversation_id": "00000000-0000-0000-0000-000000000000"
            },
            "id": "test-1"
        }
        
        resp = await client.post(f"{NEXUS_URL}/invoke", json=payload, headers={"X-Budget-USD": "1.0"})
        
        if resp.status_code != 200:
            console.print(f"[red]Request failed: {resp.status_code}[/red]")
            console.print(resp.text)
            return

        data = resp.json()
        if "error" in data:
            console.print(f"[red]RPC Error: {data['error']}[/red]")
            return

        result = data.get("result", {})
        agent = result.get("agent")
        response = result.get("response")
        
        console.print(Panel(json.dumps(result, indent=2), title="Response"))
        
        if agent == expected_agent:
            console.print(f"[green]✔ Correctly routed to {agent}[/green]")
        else:
            console.print(f"[yellow]⚠ Expected {expected_agent}, got {agent}[/yellow]")

    except Exception as e:
        console.print(f"[red]Error testing orchestration: {str(e)}[/red]")

async def main():
    console.print("[bold]Genesis NGX - Local Integration Test[/bold]")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Health Checks
        nexus_ok = await check_health(client, "Nexus", NEXUS_URL)
        fitness_ok = await check_health(client, "Fitness", FITNESS_URL)
        nutrition_ok = await check_health(client, "Nutrition", NUTRITION_URL)
        
        if not (nexus_ok and fitness_ok and nutrition_ok):
            console.print("\n[bold red]⚠ Some services are down. Aborting tests.[/bold red]")
            console.print("Run: [bold]docker-compose up --build[/bold]")
            return

        # 2. Test Nexus Direct (General)
        await test_orchestration(client, "Hola, ¿cómo estás?", "nexus")

        # 3. Test Fitness Handoff
        await test_orchestration(client, "Quiero planificar una rutina de ejercicios para espalda", "fitness")
        
        # 4. Test Nutrition Handoff
        await test_orchestration(client, "Necesito una dieta baja en carbohidratos", "nutrition")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
