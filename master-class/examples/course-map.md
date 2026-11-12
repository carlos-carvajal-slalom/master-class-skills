# Mapa del curso: Lab 02 (Tool Use + MCP)

## Intención del lab
Un LLM sólo produce texto. Este lab enseña cómo convertirlo en algo que **actúa en el mundo real sin perder el control**: el modelo *pide*, tu código *decide y ejecuta*; ese intercambio repetido es un agente. Luego, cuando muchas apps necesitan las mismas herramientas, MCP las saca a un servidor compartido, y eso trae sus propias reglas de seguridad.

Al terminar deberías poder **decidir**: qué herramienta diseñar y cómo, qué hacer cuando falla, cuándo es seguro reintentar, cuándo vale la pena MCP (y cuándo no), y qué revisar antes de conectar un servidor ajeno.

## Lectura (profundidad acotada)

| Nivel | Leído | Motivo |
|---|---|---|
| 0 | `01 - Tool Use & Function Calling.md`, `02 - MCP Fundamentals.md` (conceptos, errores comunes, self-check, ejercicios) | Núcleo del lab |
| 0 | Notebooks: no se leyeron celda por celda | Reflejan el walkthrough de las notas; el código sólo se usa como evidencia |
| 1 | What is tool use?, What is an agent?, The agent loop in code, Writing Tools for Agents, MCP (Model Context Protocol), AgentCore Gateway | Prerrequisitos declarados por el lab |
| 2 | OpenAPI-spec'd APIs as Tools | Responde "¿existe algo mejor que MCP?" |

**Descartado:** labs 01b, 03, 05–10 (prerrequisitos ya cursados o temas futuros); patrones de agentes (Router, Swarm…), frameworks (Strands, LangGraph), otros tipos de herramienta (Code Interpreter, BrowserUse…), AgentCore Runtime/Harness/Registry: tangenciales a la intención.

## Lecciones (cadena de problemas)

| # | Lección | Problema que abre | Idea errónea a desmontar | Analogía / apertura | Resuelve → deja abierto |
|---|---|---|---|---|---|
| 0 | **El panorama** | "¿Cuánto me devuelven por la orden A-1005?" y el modelo inventa una cifra con total seguridad | "El modelo sabe / puede consultar" | Escena: el cliente de Ridgeline | Mapa del recorrido |
| 1 | **El modelo no ejecuta nada** | Un modelo atrapado en texto necesita datos frescos y acciones | "El modelo corrió nuestra consulta SQL y borró filas" | Tu ESP32 con el control infrarrojo: el control sólo emite códigos; el receptor decide qué hace | Una pregunta necesita varios pasos → |
| 2 | **El loop: de una llamada a un agente** | Consultar la orden *y luego* calcular el reembolso | "El modelo recuerda la conversación" / "el loop vive en el modelo" | El recorrido de un mensaje por el loop | ¿Por qué elige mal la herramienta? → |
| 3 | **Herramientas que el modelo entiende** | El modelo llama a la herramienta equivocada o inventa argumentos | "Más herramientas = agente más capaz"; "una herramienta por endpoint" | La descripción es un prompt (SWE-bench: el salto vino de las descripciones, no del modelo) | ¿Y cuando la herramienta falla? → |
| 4 | **El error es información, no un crash** | Una orden que no existe tumba el notebook | "Las excepciones deben subir" | Los 4 tipos de falla y qué ve el modelo en cada uno | ¿Puedo simplemente reintentar? → |
| 5 | **Reintentar sin pagar dos veces** | Un reembolso que se pagó dos veces | "Reintentar siempre da más confiabilidad" | El botón del elevador (presionar dos veces = una sola llamada) | Si el modelo puede ser engañado… → |
| 6 | **Tus herramientas son tu radio de explosión** | Un ticket con una instrucción escondida | "Un system prompt más estricto lo arregla" | Lo que la herramienta puede hacer, el modelo puede ser convencido de hacerlo | ¿Cómo sé que llegó bien? → |
| 7 | **¿Llegó bien o tuvo suerte?** | Respuesta correcta ($220) por el camino equivocado | "Si la respuesta está bien, el agente está bien" | Un número: 1 respuesta correcta, 0 llamadas a la herramienta | Cinco agentes necesitan las mismas 12 herramientas → |
| 8 | **El problema N×M: por qué existe MCP** | 5 apps × 20 sistemas = 100 integraciones | "El modelo habla MCP" (no: el host traduce) | USB para periféricos; ¿no bastaba OpenAPI? | ¿Qué expone un servidor? → |
| 9 | **Tres primitivas, tres dueños** | La política de devoluciones: ¿tool, resource o prompt? | "Todo debería ser una tool" | Quién decide: modelo / app / usuario | ¿Cómo viajan los mensajes? → |
| 10 | **El cable no importa** | Mismo servidor, local y remoto, sin cambiar una línea | "Un error de herramienta es un error del protocolo" (`isError` vs JSON-RPC error) | Handshake → descubrir → llamar; stdio vs HTTP | ¿Puedo confiar en un servidor de GitHub? → |
| 11 | **Un servidor MCP es código con tus permisos** | Un colega quiere instalar hoy un "Jira MCP server" | "Si el código se ve bien, es seguro" (tool poisoning vive en las descripciones) | Instalar un servidor = instalar un paquete | Cierre → |
| 12 | **Síntesis: decidir, no memorizar** | ¿Agente o workflow? ¿Herramientas inline o MCP? | "Todo lo que use un LLM debe ser agente / MCP" | Guía de decisión; la complejidad se justifica o no se usa | — |

Notas:
- Las tool choice (`auto/any/tool`) y las llamadas paralelas van dentro de la lección 2 como límites del loop.
- La lección 12 incluye "cuándo NO usar MCP", que el lab no cubre explícitamente; se verificará con docs oficiales (web permitida).
- Cada lección varía apertura, hilo y cierre (ver `perfil-aprendiz.md`).
