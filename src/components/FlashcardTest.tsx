import { useState } from 'react'
import { Lesson } from '../lib/types'

interface FlashcardTestProps {
  lesson: Lesson
  onComplete: () => void
}

export default function FlashcardTest({ lesson, onComplete }: FlashcardTestProps) {
  const [currentCardIndex, setCurrentCardIndex] = useState(0)
  const [isFlipped, setIsFlipped] = useState(false)
  const [score, setScore] = useState(0)

  // Mock flashcard data - in production this would come from backend
  const flashcards = [
    { finnish: 'Hei', english: 'Hello', partOfSpeech: 'interjection' },
    { finnish: 'Kiitos', english: 'Thank you', partOfSpeech: 'noun' },
    { finnish: 'Kyllä', english: 'Yes', partOfSpeech: 'adverb' },
    { finnish: 'Ei', english: 'No', partOfSpeech: 'adverb' },
    { finnish: 'Yksi', english: 'One', partOfSpeech: 'numeral' },
  ]

  const currentCard = flashcards[currentCardIndex]
  const progress = ((currentCardIndex + 1) / flashcards.length) * 100

  const handleKnow = () => {
    setScore(score + 1)
    handleNext()
  }

  const handleDontKnow = () => {
    handleNext()
  }

  const handleNext = () => {
    if (currentCardIndex < flashcards.length - 1) {
      setCurrentCardIndex(currentCardIndex + 1)
      setIsFlipped(false)
    } else {
      handleTestComplete()
    }
  }

  const handleTestComplete = () => {
    const accuracy = Math.round((score / flashcards.length) * 100)
    alert(`Test Complete! Score: ${score}/${flashcards.length} (${accuracy}%)`)
    onComplete()
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">{lesson.title}</h1>
          <p className="text-gray-600">{lesson.description}</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8 bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-600">
              Card {currentCardIndex + 1} of {flashcards.length}
            </span>
            <span className="text-sm font-medium text-gray-600">
              Score: {score}/{flashcards.length}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-indigo-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Flashcard */}
        <div className="mb-8">
          <div
            onClick={() => setIsFlipped(!isFlipped)}
            className="relative w-full h-80 cursor-pointer perspective"
          >
            <div
              className={`relative w-full h-full transition-transform duration-500 transform ${
                isFlipped ? 'rotate-y-180' : ''
              }`}
              style={{
                transformStyle: 'preserve-3d',
                transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
              }}
            >
              {/* Front of card */}
              <div
                className="absolute w-full h-full bg-white rounded-lg shadow-lg p-8 flex flex-col items-center justify-center"
                style={{ backfaceVisibility: 'hidden' }}
              >
                <p className="text-sm text-gray-500 mb-4">FINNISH</p>
                <p className="text-5xl font-bold text-indigo-600 mb-4">{currentCard.finnish}</p>
                <p className="text-gray-500 text-center">Click to reveal English</p>
              </div>

              {/* Back of card */}
              <div
                className="absolute w-full h-full bg-indigo-600 rounded-lg shadow-lg p-8 flex flex-col items-center justify-center"
                style={{
                  backfaceVisibility: 'hidden',
                  transform: 'rotateY(180deg)',
                }}
              >
                <p className="text-sm text-indigo-200 mb-4">ENGLISH</p>
                <p className="text-5xl font-bold text-white mb-4">{currentCard.english}</p>
                <p className="text-indigo-100 text-sm text-center">
                  {currentCard.partOfSpeech}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            onClick={handleDontKnow}
            className="flex-1 px-6 py-4 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium text-lg"
          >
            Don't Know
          </button>
          <button
            onClick={handleKnow}
            className="flex-1 px-6 py-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium text-lg"
          >
            Know It
          </button>
        </div>
      </div>
    </div>
  )
}
