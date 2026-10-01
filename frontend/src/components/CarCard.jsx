import { formatPriceINR } from '../utils/formatPrice'

/**
 * Reusable card that shows the key structured fields for one car.
 */
function CarCard({ car }) {
  return (
    <article className="border border-slate-200 bg-white p-5 text-left shadow-sm">
      <h3 className="text-lg font-semibold text-slate-900">
        {car.brand} {car.model}
      </h3>
      <p className="text-sm text-slate-500">{car.variant}</p>

      <p className="mt-3 text-xl font-bold text-slate-900">
        {formatPriceINR(car.price)}
      </p>

      <div className="mt-3 flex flex-wrap gap-2 text-sm text-slate-700">
        <span className="bg-slate-100 px-2 py-1">{car.body_type}</span>
        <span className="bg-slate-100 px-2 py-1">{car.fuel_type}</span>
        <span className="bg-slate-100 px-2 py-1">{car.transmission}</span>
      </div>

      <div className="mt-3 space-y-1 text-sm text-slate-600">
        <p>{car.mileage} km/l</p>
        <p>{car.seating_capacity} Seats</p>
        <p className="font-medium text-slate-800">
          Safety: {car.safety_rating}/5
        </p>
      </div>
    </article>
  )
}

export default CarCard
