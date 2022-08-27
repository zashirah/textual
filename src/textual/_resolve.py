from __future__ import annotations

from itertools import accumulate
from fractions import Fraction
from typing import cast

from .geometry import Size
from .css.scalar import Scalar


def resolve(
    dimensions: list[Scalar],
    total: int,
    gutter: int,
    size: Size,
    viewport: Size,
) -> list[tuple[int, int]]:
    """Resolve a list of dimensions.

    Args:
        dimensions (list[Scalar]): A list of scalars for column / row sizes.
        total (int): Total space to divide.
        gutter (int): Gutter between rows / columns.
        size (Size): Size of container.
        viewport (Size): Size of viewport.

    Returns:
        list[tuple[int, int]]: List of (<OFFSET>, <LENGTH>)
    """

    resolved: list[Fraction | Scalar] = [
        scalar if scalar.is_fraction else scalar.resolve_dimension(size, viewport)
        for scalar in dimensions
    ]
    from_float = Fraction.from_float
    total_fraction = from_float(
        sum(dimension.value for dimension in resolved if isinstance(dimension, Scalar))
    )

    if total_fraction:
        total_gutter = gutter * (len(dimensions) - 1)
        consumed = sum(
            dimension for dimension in resolved if isinstance(dimension, Fraction)
        )
        remaining = max(Fraction(0), Fraction(total - total_gutter) - consumed)
        if remaining:
            fraction_unit = Fraction(remaining, total_fraction)
            resolved = [
                (
                    from_float(dimension.value) * fraction_unit
                    if isinstance(dimension, Scalar)
                    else dimension
                )
                for dimension in resolved
            ]

    resolved_fractions: list[Fraction] = cast("list[Fraction]", resolved)
    fraction_gutter = Fraction(gutter)
    offsets = [0] + [
        int(fraction)
        for fraction in accumulate(
            value
            for fraction in resolved_fractions
            for value in (fraction, fraction_gutter)
        )
    ]

    results = list(
        zip(
            offsets[::2],
            [
                offset2 - offset1
                for offset1, offset2 in zip(offsets[::2], offsets[1::2])
            ],
        )
    )
    return results


if __name__ == "__main__":

    dimensions = [Scalar.parse("3"), Scalar.parse("1fr"), Scalar.parse("1")]

    print(resolve(dimensions, 20, 1, Size(40, 20), Size(40, 20)))

    print(
        resolve(
            [Scalar.parse("1fr"), Scalar.parse("1fr")],
            20,
            1,
            Size(40, 20),
            Size(40, 20),
        )
    )

    print(
        resolve(
            [
                Scalar.parse("1fr"),
            ],
            20,
            1,
            Size(40, 20),
            Size(40, 20),
        )
    )
