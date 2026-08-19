# Reto de Negocio: Recomendación a la Gerencia

**Decisión recomendada:** 
Mantener la infraestructura actual (escala vertical) durante el próximo año y presupuestar la transición a un entorno distribuido a mediano plazo para el manejo masivo de la contratación pública.

**Salida ante la saturación:** 
Actualmente, nuestra capacidad de memoria nos permite procesar la analítica de expedientes en una sola máquina. Sin embargo, al alcanzar el límite, la opción técnica sustentada será distribuir el almacenamiento y procesamiento (clúster), dado que no podemos reducir arbitrariamente el volumen de los datos ni eliminar columnas sin perder trazabilidad probatoria y alcance en la auditoría legal.

**Cifras de soporte:** 
Nuestra muestra representativa ocupa **0.3045 GB** en disco físico, pero al cargarse en la plataforma analítica se expande **3.01 veces** su tamaño original. Contando con una memoria útil real proyectada de **11.20 GB** en los equipos de análisis y una tasa de crecimiento estimada del 5% mensual en los procesos de contratación, el sistema colapsará matemáticamente en **51.3 meses**.

**Horizonte y sensibilidad:** 
Esta recomendación es válida por los próximos tres años. Si la adopción del SECOP II creciera al doble (10% mensual), nuestro margen de maniobra se reduciría casi a la mitad, obligando a adelantar drásticamente la inversión en infraestructura distribuida.

---
*Declaración del uso de IA: Documento estructurado y redactado con la asistencia de Gemini. Todas las cifras reportadas de factor de expansión ($k$), tamaño en disco ($S_0$) y proyección de saturación provienen exclusivamente de ejecuciones reales de código realizadas por el equipo sobre los conjuntos de datos oficiales.*