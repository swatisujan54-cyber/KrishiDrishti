import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { cropsApi } from '../api/crops'
import { scansApi } from '../api/scans'
import type { Advisory, Crop, Scan } from '../api/types'
import { useAuth } from '../context/AuthContext'
import Alert from '../components/ui/Alert'
import Button from '../components/ui/Button'
import Spinner from '../components/ui/Spinner'
import PredictionCard from '../components/scan/PredictionCard'
import AdvisoryCard from '../components/scan/AdvisoryCard'

type Step = 'select-crop' | 'upload-image' | 'predicting' | 'result' | 'error'

export default function ScanPage() {
  const { user } = useAuth()
  const navigate   = useNavigate()
  const [crops,     setCrops]     = useState<Crop[]>([])
  const [cropId,    setCropId]    = useState<number | null>(null)
  const [selectedCrop, setSelectedCrop] = useState<Crop | null>(null)
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [preview,   setPreview]   = useState<string | null>(null)
  const [step,      setStep]      = useState<Step>('select-crop')
  const [scan,      setScan]      = useState<Scan | null>(null)
  const [advisory,  setAdvisory]  = useState<Advisory | null>(null)
  const [errorMsg,  setErrorMsg]  = useState('')

  const lang = user?.preferred_language ?? 'en'

  useEffect(() => {
    cropsApi.list().then((p) => setCrops(p.items)).catch(() => {})
  }, [])

  function handleCropSelect(crop: Crop) {
    setCropId(crop.id)
    setSelectedCrop(crop)
    setStep('upload-image')
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setImageFile(file)
    setPreview(URL.createObjectURL(file))
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (!file) return
    setImageFile(file)
    setPreview(URL.createObjectURL(file))
  }

  async function handleSubmit() {
    if (!cropId || !imageFile) return
    setStep('predicting')
    setErrorMsg('')
    try {
      const result = await scansApi.create(cropId, imageFile)
      setScan(result)
      if (result.disease_id) {
        try {
          const adv = await scansApi.getAdvisory(result.disease_id, lang)
          setAdvisory(adv)
        } catch { /* advisory not critical */ }
      }
      setStep('result')
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail ?? 'Could not process the image. Please try again.')
      setStep('error')
    }
  }

  function handleReset() {
    setCropId(null)
    setSelectedCrop(null)
    setImageFile(null)
    setPreview(null)
    setScan(null)
    setAdvisory(null)
    setStep('select-crop')
    setErrorMsg('')
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-earth-900 mb-2">Check Your Crop</h1>
      <p className="text-sm text-earth-500 mb-8">
        Select your crop, then upload a clear photo of the affected leaf.
      </p>

      {/* STEP 1 — Crop selection */}
      {step === 'select-crop' && (
        <div>
          <h2 className="text-sm font-semibold text-earth-700 mb-1">Which crop are you checking?</h2>
          <p className="text-xs text-earth-400 mb-4">
            Crops marked "limited" don't have full disease model support yet.
          </p>
          {crops.length === 0 ? (
            <Spinner label="Loading crops…" />
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {crops.map((c) => (
                <button
                  key={c.id}
                  onClick={() => handleCropSelect(c)}
                  className={`
                    flex flex-col items-start gap-1 rounded-lg border p-4 text-left
                    transition-colors duration-150
                    ${c.is_supported
                      ? 'border-cream-300 bg-white hover:border-brand-400 hover:bg-brand-50/50 text-earth-800'
                      : 'border-cream-200 bg-cream-100/50 hover:border-earth-300 text-earth-500'
                    }
                  `}
                >
                  <span className="font-medium text-sm">{c.name}</span>
                  {c.is_supported ? (
                    <span className="text-xs text-brand-500">{c.disease_count} diseases known</span>
                  ) : (
                    <span className="text-xs text-earth-400">Limited support</span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* STEP 2 — Image upload */}
      {step === 'upload-image' && (
        <div>
          <button
            onClick={() => setStep('select-crop')}
            className="text-sm text-brand-600 hover:underline mb-4 flex items-center gap-1"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Change crop
          </button>

          {selectedCrop && (
            <div className="mb-4 p-3 bg-brand-50 border border-brand-200 rounded-lg">
              <p className="text-sm text-earth-700">
                <strong className="text-brand-700">{selectedCrop.name}</strong>
                {selectedCrop.scientific_name && (
                  <span className="text-earth-400 italic"> — {selectedCrop.scientific_name}</span>
                )}
              </p>
              {selectedCrop.description && (
                <p className="text-xs text-earth-500 mt-1">{selectedCrop.description}</p>
              )}
            </div>
          )}

          <h2 className="text-sm font-semibold text-earth-700 mb-3">
            Upload a photo of the affected leaf
          </h2>

          {/* Drop zone */}
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className={`
              relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer
              transition-colors duration-150
              ${preview ? 'border-brand-400 bg-brand-50/50' : 'border-cream-300 bg-white hover:border-brand-400 hover:bg-brand-50/30'}
            `}
          >
            {preview ? (
              <img
                src={preview}
                alt="Leaf preview"
                className="mx-auto max-h-64 rounded-lg object-contain"
              />
            ) : (
              <div className="flex flex-col items-center gap-3 py-8">
                <svg className="h-10 w-10 text-earth-300" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-earth-600">
                    Click to select a photo
                  </p>
                  <p className="text-xs text-earth-400 mt-1">
                    or drag and drop here — JPEG or PNG, max 10 MB
                  </p>
                </div>
                <p className="text-xs text-earth-400 mt-2 max-w-xs">
                  For best results, take a clear, well-lit photo of a single affected leaf.
                </p>
              </div>
            )}
            <input
              type="file"
              accept="image/jpeg,image/png"
              onChange={handleFileChange}
              className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
              aria-label="Upload crop image"
            />
          </div>

          {imageFile && (
            <p className="text-xs text-earth-400 mt-2">{imageFile.name} ({(imageFile.size / 1024).toFixed(0)} KB)</p>
          )}

          <Button
            onClick={handleSubmit}
            disabled={!imageFile}
            size="lg"
            className="w-full mt-5"
          >
            Analyse image
          </Button>
        </div>
      )}

      {/* STEP 3 — Predicting */}
      {step === 'predicting' && (
        <div className="py-12">
          <Spinner label="Analysing your crop image… this may take a moment." />
        </div>
      )}

      {/* STEP 4 — Result */}
      {step === 'result' && scan && (
        <div className="flex flex-col gap-5">
          <PredictionCard scan={scan} />
          {advisory && <AdvisoryCard advisory={advisory} />}
          <div className="flex gap-3 mt-2">
            <Button onClick={handleReset} variant="secondary">
              Check another crop
            </Button>
            <Button onClick={() => navigate('/history')} variant="ghost">
              View my scans
            </Button>
          </div>
        </div>
      )}

      {/* ERROR */}
      {step === 'error' && (
        <div className="flex flex-col gap-4">
          <Alert kind="error" title="Could not analyse image">
            {errorMsg}
          </Alert>
          <Button onClick={handleReset} variant="secondary">
            Try again
          </Button>
        </div>
      )}
    </div>
  )
}
