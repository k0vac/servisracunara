export function formatMoney(value: string | number) {
  const amount = typeof value === 'number' ? value : Number(value)
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: 'RSD',
    minimumFractionDigits: 2,
  }).format(Number.isFinite(amount) ? amount : 0)
}
