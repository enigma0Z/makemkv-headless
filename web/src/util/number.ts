export const takeGreater = (
  a: number | undefined | null, 
  b: number | undefined | null
): number | undefined => {
  if (a && b) {
    if (a > b) return a;
    else return b;
  } else if (a !== undefined && a !== null) {
    return a
  } else if (b !== undefined && b !== null) {
    return b
  }

  return undefined
}