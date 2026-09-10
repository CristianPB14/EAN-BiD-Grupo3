"""
T9 - Matriz ponderada para decidir el paradigma de almacenamiento.

Opciones:
    - Almacén de datos
    - Lago de datos
    - Lakehouse

Escala de calificación:
    1 = muy desfavorable
    2 = desfavorable
    3 = aceptable
    4 = favorable
    5 = muy favorable

El puntaje final se obtiene mediante:

    puntaje = sum(peso * calificacion / 100)
"""


CRITERIOS = [
    "Flexibilidad de formatos",
    "Costo de almacenamiento",
    "Calidad y gobierno del dato",
    "Rendimiento analítico",
    "Necesidad de transacciones",
    "Complejidad operativa",
]


# Los pesos suman exactamente 100 %.
PESOS = {
    "Flexibilidad de formatos": 20,
    "Costo de almacenamiento": 20,
    "Calidad y gobierno del dato": 20,
    "Rendimiento analítico": 15,
    "Necesidad de transacciones": 10,
    "Complejidad operativa": 15,
}


CALIFICACIONES = {
    "Almacén": {
        "Flexibilidad de formatos": 2,
        "Costo de almacenamiento": 3,
        "Calidad y gobierno del dato": 5,
        "Rendimiento analítico": 5,
        "Necesidad de transacciones": 3,
        "Complejidad operativa": 3,
    },

    "Lago": {
        "Flexibilidad de formatos": 5,
        "Costo de almacenamiento": 5,
        "Calidad y gobierno del dato": 3,
        "Rendimiento analítico": 4,
        "Necesidad de transacciones": 2,
        "Complejidad operativa": 4,
    },

    "Lakehouse": {
        "Flexibilidad de formatos": 5,
        "Costo de almacenamiento": 4,
        "Calidad y gobierno del dato": 5,
        "Rendimiento analítico": 5,
        "Necesidad de transacciones": 2,
        "Complejidad operativa": 2,
    },
}


def validar_pesos():
    """Comprueba que los pesos sumen 100 %."""
    total = sum(PESOS.values())

    if total != 100:
        raise ValueError(
            f"Los pesos deben sumar 100 %. Actualmente suman {total}%."
        )


def calcular_puntaje(opcion):
    """
    Calcula el puntaje ponderado de una opción.

    Fórmula:
        peso (%) * calificación / 100
    """
    puntaje = 0

    for criterio in CRITERIOS:
        peso = PESOS[criterio]
        calificacion = CALIFICACIONES[opcion][criterio]

        puntaje += peso * calificacion / 100

    return puntaje


def mostrar_matriz():
    """Imprime la matriz completa en consola."""

    print("\nMATRIZ PONDERADA - T9")
    print("=" * 90)

    print(
        f"{'Criterio':35}"
        f"{'Peso':>8}"
        f"{'Almacén':>12}"
        f"{'Lago':>12}"
        f"{'Lakehouse':>14}"
    )

    print("-" * 90)

    for criterio in CRITERIOS:
        print(
            f"{criterio:35}"
            f"{PESOS[criterio]:>7}%"
            f"{CALIFICACIONES['Almacén'][criterio]:>12}"
            f"{CALIFICACIONES['Lago'][criterio]:>12}"
            f"{CALIFICACIONES['Lakehouse'][criterio]:>14}"
        )

    print("-" * 90)

    resultados = {}

    for opcion in CALIFICACIONES:
        resultados[opcion] = calcular_puntaje(opcion)

    for opcion, puntaje in resultados.items():
        print(f"{opcion:15}: {puntaje:.2f} / 5.00")

    ganador = max(resultados, key=resultados.get)

    print("-" * 90)
    print(f"DECISIÓN SUGERIDA POR LA MATRIZ: {ganador}")


def main():
    """Punto de entrada del programa."""

    validar_pesos()
    mostrar_matriz()


if __name__ == "__main__":
    main()
