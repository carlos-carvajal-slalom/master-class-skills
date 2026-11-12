# Fase 1 — Cómo enseñar bien en video (base para la skill)

Leyenda de evidencia: **[E]** evidencia experimental sólida · **[P]** práctica de creadores / opinión experta.

---

## 1. Principios (accionables)

| # | Regla | Por qué funciona | Fuente |
|---|---|---|---|
| 1 | **Problema antes que solución.** Cada lección abre con una situación concreta donde algo duele o falla, y sólo después nombra el concepto. | Si primero ves el "hueco" en lo que sabes, la explicación tiene dónde aterrizar. "Decirlo" funciona mucho mejor cuando antes se experimentó el problema. | Schwartz & Bransford, *A Time for Telling* (1998) [E]; Kapur, *Productive Failure* (2008+) [E] |
| 2 | **Abre una pregunta y ciérrala tarde.** Plantea al inicio una pregunta concreta que el espectador quiera resolver; respóndela al final de la lección. | La curiosidad nace al percibir un vacío de información específico; mantiene la atención mientras el vacío siga abierto. | Loewenstein, *Information Gap Theory of Curiosity* (1994) [E] |
| 3 | **Ataca el modelo mental equivocado, no sólo expliques el correcto.** Di explícitamente "lo que uno pensaría es X… y por esto es incorrecto". | En física, videos "claros" hacían que la gente se sintiera segura sin aprender; videos que presentaban y desmontaban la idea errónea parecían más confusos pero producían mucho más aprendizaje. | Muller, tesis doctoral U. Sydney (2008) [E] |
| 4 | **Concreto → abstracto.** Ejemplo específico primero, generalización después, nombre técnico al final. | El nombre sin intuición es una etiqueta vacía; la intuición hace que el nombre "se pegue". | Sanderson / 3Blue1Brown [P]; consistente con Mayer *pre-training* [E] |
| 5 | **"Lo habrías inventado tú".** Reconstruye la solución como si el espectador la diseñara: "¿qué harías tú? … ok, eso falla porque… entonces…". | Convierte la explicación en razonamiento, no en memorización; deja ver cómo piensa un experto. | Sanderson / 3Blue1Brown, Karpathy "from scratch" [P] |
| 6 | **Coherencia: quita todo lo que no sirve al objetivo de la lección.** Nada de detalles interesantes-pero-irrelevantes, código accesorio o decoración. | El material extra compite por memoria de trabajo y reduce el aprendizaje. | Mayer, *coherence principle* [E]; Sweller, carga cognitiva [E] |
| 7 | **Señaliza la estructura.** Di dónde estamos y hacia dónde vamos ("ya vimos por qué falla; ahora veamos qué lo arregla"). Resalta en pantalla lo que se está diciendo. | Ayuda a organizar la información en un modelo mental. | Mayer, *signaling principle* [E] |
| 8 | **Narración + visual, no narración + texto idéntico.** La pantalla muestra diagramas/ejemplos; no repite la narración como texto. | Leer y escuchar lo mismo satura el mismo canal; imagen + voz usa dos canales. | Mayer, *modality* y *redundancy principles* [E] |
| 9 | **Segmenta en lecciones con un solo objetivo cada una.** El curso puede durar lo que haga falta; cada lección cubre una idea y termina. | El engagement cae claramente en videos largos sin cortes; dividir en segmentos controlables mejora el aprendizaje. | Guo, Kim & Rubin, edX 6.9M sesiones (2014) [E]; Mayer, *segmenting* [E] |
| 10 | **Tono conversacional, primera y segunda persona, entusiasmo real.** "Tú", "nosotros", hablar rápido y con energía, no leer. | Estilo personal mejora la transferencia; en edX, instructores que hablaban rápido y con entusiasmo retenían más. | Mayer, *personalization principle* [E]; Guo et al. 2014 [E] |
| 11 | **Dibujo progresivo > slides estáticos.** Construir el diagrama paso a paso mientras se explica. | Videos estilo tablet (Khan) fueron más atractivos que slides; la construcción progresiva aplica *temporal contiguity*. | Guo et al. 2014 [E]; Mayer [E] |
| 12 | **El código es evidencia, no protagonista.** Muestra el fragmento mínimo que prueba el concepto ya explicado; nunca recorridos línea por línea. | Los worked examples ayudan a novatos, pero sólo si cada paso conecta con el principio; el detalle irrelevante es carga extrínseca. | Sweller, *worked example effect* [E]; Mayer coherence [E] |
| 13 | **Haz recordar, no sólo escuchar.** Pausas con pregunta ("antes de seguir: ¿qué pasaría si…?") y recap que pide predecir, no repetir. | Recuperar de memoria consolida mucho más que reexponerse al material. | Roediger & Karpicke (2006), *testing effect* [E] |
| 14 | **Cuándo NO usarlo.** Cada concepto cierra con sus límites, trade-offs y alternativas. | Saber los límites es lo que separa entender de memorizar; también es la forma más fuerte de "por qué". | Práctica experta (ByteByteGo, system design) [P] |
| 15 | **Hilo narrativo entre lecciones.** Cada lección termina con el problema que la siguiente resuelve. | Convierte el curso en una historia de "problema → solución → nuevo problema"; mantiene el open loop entre segmentos. | Loewenstein [E]; estructura de Veritasium/3B1B [P] |

---

## 2. Anti-patrones

| Anti-patrón | Por qué falla | Visto en `Lab 02/masterclass` |
|---|---|---|
| Lista de viñetas narrada (frases sueltas de 3–4 s) | No hay razonamiento que seguir; suena a lectura. | ✅ todas las lecciones |
| Abrir con definición | No hay motivo para que importe; no se abre ningún vacío de curiosidad. | ✅ "A language model does not read words the way we do" |
| Explicar el "cómo" sin el "qué" ni el "por qué" | Fórmulas sin problema: se olvida y no se transfiere. | ✅ |
| Explicación "clara" sin confrontar la idea errónea | Da falsa sensación de entender (Muller). | ✅ |
| Recorrido de código línea por línea | Carga cognitiva extrínseca; convierte la clase en tutorial de programación. | — (riesgo explícito) |
| Texto en pantalla = narración | Redundancia. | Parcial |
| Lecciones aisladas sin puente | Sin hilo, sin motivo para ver la siguiente. | ✅ |
| Duración fija impuesta por el formato | El contenido se recorta para encajar; queda superficial. | ✅ ~72 s por lección |
| Afirmaciones sin ejemplo concreto | Abstracción sin anclaje. | ✅ |
| Preguntas retóricas sin pausa ni respuesta | Parecen interacción pero no obligan a pensar. | ✅ "Predict: can fluent wording prove…" sin desarrollo |

---

## 3. Proceso para leer el material

1. **Inventario:** listar todos los archivos del lab (notebooks, código, notas, enlaces).
2. **Lectura con profundidad acotada:** lab → referencias directas (nivel 1) → referencias de esas notas (nivel 2). No más. Sólo seguir lo relevante para la intención del lab; registrar leído / descartado / motivo.
3. **Extraer la intención:** responder en 2–3 frases "¿qué debería poder *entender y decidir* alguien al terminar este lab?" (no "qué código escribió").
4. **Mapa de conceptos:** para cada concepto: problema que resuelve · idea errónea común · intuición/analogía · límites / cuándo no usarlo · evidencia en el código del lab (si aplica).
5. **Ordenar por dependencia de problemas:** cada concepto debe resolver un dolor que el anterior dejó expuesto.

---

## 4. Estructura del curso

- **Lección 0 — El panorama:** qué problema grande ataca el curso completo y qué vas a poder hacer/decidir al final. Mapa visual del recorrido.
- **Lecciones 1…N:** una idea cada una, ordenadas como cadena de problemas ("resolvimos A, pero ahora aparece B").
- **Lección final — Síntesis:** reconstruir el panorama completo, decisiones de diseño, cuándo usar qué, y preguntas de autoevaluación.
- Duración: libre. Regla: si una lección necesita dos objetivos de aprendizaje, son dos lecciones.

---

## 5. Plantilla de lección

1. **Gancho / problema** — situación concreta donde algo falla o duele. Pregunta abierta explícita.
2. **Por qué importa** — consecuencia real de no resolverlo.
3. **El intento ingenuo** — lo que uno haría primero y por qué no funciona (idea errónea).
4. **Intuición / analogía** — construir la idea con algo familiar.
5. **El concepto** — ahora sí, el nombre técnico y la definición precisa.
6. **Ejemplo** — caso concreto; código sólo si prueba algo y sólo el fragmento mínimo.
7. **Límites** — errores comunes, trade-offs, cuándo no usarlo.
8. **Pausa de recuperación** — pregunta para que el espectador prediga o explique.
9. **Recap** — cerrar la pregunta del gancho.
10. **Puente** — el problema nuevo que resuelve la siguiente lección.

---

## 6. Formato del guion

| Narración | En pantalla | Propósito |
|---|---|---|
| Texto hablado, conversacional, completo. | Lo que se dibuja/muestra (no repetir la narración). | Qué principio cumple (gancho, idea errónea, intuición, recuperación…). |

---

## 7. Rúbrica de calidad (cada guion debe pasar todo)

- [ ] ¿La lección abre con un problema concreto, no con una definición?
- [ ] ¿Se explica el **por qué** antes del **cómo**?
- [ ] ¿Alguien que nunca vea el código entiende el concepto?
- [ ] ¿Se presenta y desmonta al menos una idea errónea?
- [ ] ¿Hay al menos un ejemplo concreto antes de la abstracción?
- [ ] ¿La pregunta del gancho se responde explícitamente?
- [ ] ¿Hay al menos una pausa de recuperación real?
- [ ] ¿Se explican los límites / cuándo no usarlo?
- [ ] ¿El código mostrado (si hay) es mínimo y prueba algo ya explicado?
- [ ] ¿La pantalla complementa la narración en vez de repetirla?
- [ ] ¿Leído en voz alta suena a profesor hablando, no a viñetas?
- [ ] ¿Termina con un puente a la siguiente lección?
- [ ] ¿Cada frase sirve al objetivo de la lección (coherencia)?

---

## 8. Preguntas abiertas para ti

1. **Formato visual:** ¿seguimos con el renderer de Excalidraw (voz + dibujo progresivo) o primero sólo guion y el formato después?
2. **Voz/persona:** ¿narrador neutro, o un "profesor" con personalidad (humor, anécdotas)?
3. **Nivel de partida:** ¿asumimos que sabes programar y conoces LLMs a nivel usuario, o partimos de cero?
4. **Interactividad:** ¿las pausas de recuperación deben ser sólo narradas o también un quiz al final de cada lección?
5. **Referencias externas:** además de tus notas, ¿el agente puede buscar en la web (docs oficiales, specs) para completar el "por qué"?

---

## Fuentes

- Guo, Kim, Rubin (2014). *How Video Production Affects Student Engagement: An Empirical Study of MOOC Videos.* ACM L@S. https://doi.org/10.1145/2556325.2566239
- Mayer, R. E. *Multimedia Learning* (3rd ed., 2020) — 12 principios (coherence, signaling, redundancy, spatial/temporal contiguity, segmenting, pre-training, modality, personalization, voice, embodiment, image).
- Muller, D. A. (2008). *Designing Effective Multimedia for Physics Education.* PhD thesis, University of Sydney.
- Schwartz, D. L. & Bransford, J. D. (1998). *A Time for Telling.* Cognition and Instruction 16(4).
- Kapur, M. (2008). *Productive Failure.* Cognition and Instruction 26(3).
- Loewenstein, G. (1994). *The Psychology of Curiosity: A Review and Reinterpretation.* Psychological Bulletin 116(1).
- Roediger, H. L. & Karpicke, J. D. (2006). *Test-Enhanced Learning.* Psychological Science 17(3).
- Sweller, J. — Cognitive Load Theory; worked example effect; Kalyuga — expertise reversal effect.
- Sanderson, G. (3Blue1Brown) — entrevistas y videos; Karpathy, A. — serie "Neural Networks: Zero to Hero". [práctica]
