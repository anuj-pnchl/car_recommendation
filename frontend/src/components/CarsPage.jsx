import { useEffect, useState } from 'react'
import CarCard from './CarCard'
import { API_BASE_URL } from '../config/api'

const BODY_TYPES = ['', 'Hatchback', 'Sedan', 'SUV', 'Compact SUV', 'MPV']
const FUEL_TYPES = ['', 'Petrol', 'Diesel', 'CNG', 'Electric']
const TRANSMISSIONS = ['', 'Manual', 'Automatic', 'AMT', 'CVT', 'DCT', 'e-CVT']

/**
 * Cars listing page.
 * Fetches from GET /api/cars and supports simple structured filters.
 */
function CarsPage() {
  const [cars, setCars] = useState([])
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [bodyType, setBodyType] = useState('')
  const [fuelType, setFuelType] = useState('')
  const [transmission, setTransmission] = useState('')
  const [maxPrice, setMaxPrice] = useState('')

  useEffect(() => {
    async function fetchCars() {
      setLoading(true)
      setError('')

      try {
        const params = new URLSearchParams()
        if (bodyType) params.set('body_type', bodyType)
        if (fuelType) params.set('fuel_type', fuelType)
        if (transmission) params.set('transmission', transmission)
        if (maxPrice) params.set('max_price', maxPrice)

        const query = params.toString()
        const url = `${API_BASE_URL}/api/cars${query ? `?${query}` : ''}`

        const response = await fetch(url)
        if (!response.ok) {
          throw new Error(`Server responded with status ${response.status}`)
        }

        const data = await response.json()
        setCars(data.cars || [])
        setCount(data.count ?? 0)
      } catch {
        setCars([])
        setCount(0)
        setError(
          'Unable to load car data. Please make sure the backend is running.'
        )
      } finally {
        setLoading(false)
      }
    }

    fetchCars()
  }, [bodyType, fuelType, transmission, maxPrice])

  function clearFilters() {
    setBodyType('')
    setFuelType('')
    setTransmission('')
    setMaxPrice('')
  }

  return (
    <section className="w-full max-w-6xl mx-auto px-4 py-8">
      <div className="mb-6 text-left">
        <h2 className="text-2xl font-bold text-slate-900">Available Cars</h2>
        <p className="text-slate-600 mt-1">
          Demo dataset for learning structured filtering before RAG.
        </p>
      </div>

      {/* Simple filters — values are sent as query params to FastAPI */}
      <div className="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-5 text-left">
        <label className="block text-sm text-slate-700">
          Body Type
          <select
            className="mt-1 w-full border border-slate-300 bg-white px-3 py-2"
            value={bodyType}
            onChange={(e) => setBodyType(e.target.value)}
          >
            <option value="">All</option>
            {BODY_TYPES.filter(Boolean).map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="block text-sm text-slate-700">
          Fuel Type
          <select
            className="mt-1 w-full border border-slate-300 bg-white px-3 py-2"
            value={fuelType}
            onChange={(e) => setFuelType(e.target.value)}
          >
            <option value="">All</option>
            {FUEL_TYPES.filter(Boolean).map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="block text-sm text-slate-700">
          Transmission
          <select
            className="mt-1 w-full border border-slate-300 bg-white px-3 py-2"
            value={transmission}
            onChange={(e) => setTransmission(e.target.value)}
          >
            <option value="">All</option>
            {TRANSMISSIONS.filter(Boolean).map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="block text-sm text-slate-700">
          Max Price (INR)
          <input
            type="number"
            min="0"
            placeholder="e.g. 1500000"
            className="mt-1 w-full border border-slate-300 bg-white px-3 py-2"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
          />
        </label>

        <div className="flex items-end">
          <button
            type="button"
            onClick={clearFilters}
            className="w-full border border-slate-300 bg-white px-3 py-2 text-slate-700 hover:bg-slate-50"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {loading && <p className="text-slate-600">Loading cars…</p>}

      {error && (
        <div className="p-4 border border-red-200 bg-red-50 text-red-800 text-left">
          {error}
        </div>
      )}

      {!loading && !error && (
        <>
          <p className="mb-4 text-sm text-slate-600 text-left">
            Showing {count} car{count === 1 ? '' : 's'}
          </p>
          {count === 0 ? (
            <p className="text-slate-600 text-left">
              No cars match these filters. Try clearing or changing them.
            </p>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {cars.map((car) => (
                <CarCard key={car.id} car={car} />
              ))}
            </div>
          )}
        </>
      )}
    </section>
  )
}

export default CarsPage
