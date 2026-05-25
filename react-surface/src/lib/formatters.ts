export const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})

export const numberFormatter = new Intl.NumberFormat('en-US')

export function formatCurrency(amount: number): string {
  return currencyFormatter.format(amount)
}

export function formatNumber(value: number): string {
  return numberFormatter.format(value)
}
