/**
 * Formats an INR price for display, e.g. 1450000 → "₹14,50,000"
 * Uses the Indian numbering system (lakhs).
 */
export function formatPriceINR(price) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(price)
}
