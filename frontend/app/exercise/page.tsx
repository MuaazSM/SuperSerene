'use client'

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { 
  IconBrain, 
  IconClock,
  IconCircle,
  IconMusic,
  IconDeviceMobile,
  IconPlayerPause,
  IconPlayerPlay,
  IconPlayerStop,
  IconRefresh,
  IconCircleCheck,
  IconMoodHappy,
  IconBulb,
  IconChartBar,
  IconBook
} from "@tabler/icons-react"
import Link from "next/link"
import { cn } from "@/lib/utils"

interface Exercise {
  id: string
  title: string
  category: string
  duration: number
  description: string
  steps: string[]
}

const exercises: Exercise[] = [
  {
    id: 'box-breathing',
    title: 'Box Breathing',
    category: 'Self-Regulation',
    duration: 120, // 2 minutes in seconds
    description: 'A calming breathing technique to help manage stress and anxiety',
    steps: [
      'Inhale for 4 counts',
      'Hold for 4 counts', 
      'Exhale for 4 counts',
      'Hold for 4 counts',
      'Repeat the cycle'
    ]
  },
  {
    id: 'perspective-taking',
    title: 'Perspective Taking',
    category: 'Empathy',
    duration: 180, // 3 minutes
    description: 'Practice understanding situations from different viewpoints',
    steps: [
      'Think of a recent conflict',
      'Describe your perspective',
      'Imagine the other person\'s view',
      'Find common ground',
      'Reflect on learnings'
    ]
  },
  {
    id: 'gratitude-practice',
    title: 'Gratitude Practice',
    category: 'Self-Awareness',
    duration: 300, // 5 minutes
    description: 'Cultivate appreciation and positive emotions',
    steps: [
      'Take three deep breaths',
      'Think of something you\'re grateful for',
      'Feel the emotion deeply',
      'Express gratitude mentally',
      'Repeat with 2 more items'
    ]
  },
  {
    id: 'body-scan',
    title: 'Body Scan Meditation',
    category: 'Mindfulness',
    duration: 240, // 4 minutes
    description: 'Develop awareness of physical sensations and release tension',
    steps: [
      'Find a comfortable position',
      'Focus on your toes and feet',
      'Slowly move attention up through your legs',
      'Scan your torso, arms, and shoulders',
      'Notice your head and face',
      'Take three deep breaths and relax'
    ]
  },
  {
    id: 'grounding-technique',
    title: '5-4-3-2-1 Grounding',
    category: 'Anxiety Relief',
    duration: 150, // 2.5 minutes
    description: 'Anchor yourself to the present moment using your senses',
    steps: [
      'Name 5 things you can see',
      'Name 4 things you can physically feel',
      'Name 3 things you can hear',
      'Name 2 things you can smell',
      'Name 1 thing you can taste',
      'Notice how you feel now'
    ]
  },
  {
    id: 'emotional-check-in',
    title: 'Emotional Check-In',
    category: 'Self-Awareness',
    duration: 120, // 2 minutes
    description: 'Identify and understand your current emotional state',
    steps: [
      'Pause and breathe deeply',
      'Identify your primary emotion',
      'Notice where you feel it in your body',
      'Ask yourself why you feel this way',
      'Decide how you want to respond'
    ]
  },
  {
    id: 'progressive-relaxation',
    title: 'Progressive Muscle Relaxation',
    category: 'Stress Relief',
    duration: 300, // 5 minutes
    description: 'Release physical tension by tensing and relaxing muscle groups',
    steps: [
      'Tense your feet muscles for 5 seconds',
      'Release and notice the relaxation',
      'Move up to calves, thighs, and buttocks',
      'Continue with abdomen, chest, and arms',
      'Finish with shoulders, neck, and face',
      'Enjoy the full-body relaxation'
    ]
  },
  {
    id: 'thought-reframing',
    title: 'Thought Reframing',
    category: 'Cognitive Skills',
    duration: 180, // 3 minutes
    description: 'Transform negative thoughts into positive, realistic ones',
    steps: [
      'Identify a negative thought you\'re having',
      'Examine the evidence for and against it',
      'Challenge the thought with logic',
      'Create a more balanced perspective',
      'Notice how your mood shifts',
      'Practice this regularly'
    ]
  },
  {
    id: 'self-compassion',
    title: 'Self-Compassion Practice',
    category: 'Self-Love',
    duration: 240, // 4 minutes
    description: 'Cultivate kindness and acceptance toward yourself',
    steps: [
      'Acknowledge that you\'re struggling',
      'Remember that suffering is part of life',
      'Place your hand on your heart',
      'Offer yourself kind, supportive words',
      'Imagine a compassionate friend supporting you',
      'Feel the warmth of self-compassion'
    ]
  },
  {
    id: 'guided-visualization',
    title: 'Guided Visualization',
    category: 'Mindfulness',
    duration: 300, // 5 minutes
    description: 'Use imagination to create a calming mental environment',
    steps: [
      'Close your eyes and relax',
      'Imagine a peaceful, safe place',
      'Engage all five senses in detail',
      'Notice colors, sounds, and textures',
      'Spend time exploring this space',
      'Slowly return to the present moment'
    ]
  },
  {
    id: 'loving-kindness',
    title: 'Loving-Kindness Meditation',
    category: 'Compassion',
    duration: 240, // 4 minutes
    description: 'Develop compassion for yourself and others',
    steps: [
      'Start with yourself: "May I be happy"',
      'Extend to a loved one: "May you be happy"',
      'Include a neutral person: "May you be happy"',
      'Extend to someone difficult: "May you be happy"',
      'Include all beings: "May all be happy"',
      'Feel the expansion of compassion'
    ]
  },
  {
    id: 'mindful-breathing',
    title: 'Mindful Breathing',
    category: 'Mindfulness',
    duration: 180, // 3 minutes
    description: 'Focus on your breath to anchor yourself in the present',
    steps: [
      'Sit comfortably and close your eyes',
      'Notice your natural breathing pattern',
      'Count: "In" for 4, "Out" for 4',
      'When your mind wanders, gently return focus',
      'Maintain this rhythm for several minutes',
      'Notice the calm it brings'
    ]
  }
]

export default function ExercisePage() {
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [isComplete, setIsComplete] = useState(false)
  const [reflection, setReflection] = useState("")
  const [beforeRating, setBeforeRating] = useState<number | null>(null)
  const [afterRating, setAfterRating] = useState<number | null>(null)

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isPlaying && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(time => {
          if (time <= 1) {
            setIsPlaying(false)
            setIsComplete(true)
            return 0
          }
          return time - 1
        })
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isPlaying, timeRemaining])

  const startExercise = (exercise: Exercise) => {
    setSelectedExercise(exercise)
    setTimeRemaining(exercise.duration)
    setCurrentStep(0)
    setIsComplete(false)
    setReflection("")
    setAfterRating(null)
  }

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying)
  }

  const stopExercise = () => {
    setIsPlaying(false)
    setSelectedExercise(null)
    setTimeRemaining(0)
    setCurrentStep(0)
    setIsComplete(false)
  }

  const resetExercise = () => {
    if (selectedExercise) {
      setTimeRemaining(selectedExercise.duration)
      setCurrentStep(0)
      setIsPlaying(false)
      setIsComplete(false)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const getProgressPercentage = () => {
    if (!selectedExercise) return 0
    return ((selectedExercise.duration - timeRemaining) / selectedExercise.duration) * 100
  }

  const logProgress = () => {
    if (selectedExercise && afterRating !== null) {
      const exerciseLog = {
        date: new Date().toISOString(),
        exerciseId: selectedExercise.id,
        exerciseTitle: selectedExercise.title,
        category: selectedExercise.category,
        completed: true,
        beforeRating,
        afterRating,
        reflection
      }
      
      const existingLogs = JSON.parse(localStorage.getItem('exerciseLogs') || '[]')
      existingLogs.push(exerciseLog)
      localStorage.setItem('exerciseLogs', JSON.stringify(existingLogs))
      
      alert('Progress logged! Redirecting to dashboard...')
      setTimeout(() => {
        window.location.href = '/dashboard'
      }, 1000)
    }
  }

  // Replace your existing "if (selectedExercise && !isComplete)" block with this:

if (selectedExercise && !isComplete) {
  // Calculate which step we should be on based on time elapsed
  const totalSteps = selectedExercise.steps.length;
  const timePerStep = selectedExercise.duration / totalSteps;
  const activeStepIndex = Math.floor((selectedExercise.duration - timeRemaining) / timePerStep);
  const currentStepDisplay = Math.min(activeStepIndex, totalSteps - 1);

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center px-6 overflow-hidden relative">
      {/* Ambient Background Blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[60%] h-[60%] bg-indigo-500/10 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute -bottom-[10%] -right-[10%] w-[60%] h-[60%] bg-purple-500/10 blur-[120px] rounded-full animate-pulse" style={{ animationDelay: '2s' }} />
      </div>

      <div className="w-full max-w-2xl relative z-10 flex flex-col items-center">
        {/* Top Navigation */}
        <div className="w-full flex justify-between items-center mb-16">
          <Button 
            onClick={stopExercise}
            variant="ghost" 
            className="text-slate-500 hover:text-white hover:bg-white/5 transition-colors"
          >
            <IconPlayerStop className="mr-2 h-5 w-5" />
            End Session
          </Button>
          <div className="text-right">
            <Badge variant="outline" className="text-indigo-400 border-indigo-400/30 mb-1 uppercase tracking-tighter">
              {selectedExercise.category}
            </Badge>
          </div>
        </div>

        {/* Central Focus Ring */}
        <div className="relative w-80 h-80 flex items-center justify-center">
          {/* Pulsing breathe indicator */}
          <div 
            className={cn(
              "absolute inset-0 rounded-full border border-indigo-500/20 transition-transform duration-[4000ms] ease-in-out",
              isPlaying ? "scale-125 opacity-100" : "scale-100 opacity-20"
            )} 
          />
          
          <svg className="absolute w-full h-full transform -rotate-90" viewBox="0 0 200 200">
            <circle
              cx="100" cy="100" r="90"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="text-slate-900"
            />
            <circle
              cx="100" cy="100" r="90"
              fill="none"
              stroke="url(#zenGradient)"
              strokeWidth="3"
              strokeDasharray={`${(2 * Math.PI * 90 * getProgressPercentage()) / 100} ${2 * Math.PI * 90}`}
              className="transition-all duration-1000 ease-linear"
              strokeLinecap="round"
            />
            <defs>
              <linearGradient id="zenGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#6366f1" />
                <stop offset="100%" stopColor="#a855f7" />
              </linearGradient>
            </defs>
          </svg>

          {/* Current Instruction Text */}
          <div className="text-center px-10">
            <h2 className="text-2xl sm:text-3xl font-light text-white leading-tight tracking-tight">
              {selectedExercise.steps[currentStepDisplay]}
            </h2>
          </div>
        </div>

        {/* Timer & Controls */}
        <div className="mt-20 w-full flex flex-col items-center gap-10">
          <div className="text-center">
            <div className="text-6xl font-extralight text-white tracking-tighter tabular-nums">
              {formatTime(timeRemaining)}
            </div>
            <p className="text-slate-500 text-sm mt-2 font-medium tracking-widest uppercase">Remaining</p>
          </div>

          <div className="flex items-center gap-8">
            <Button
              onClick={resetExercise}
              variant="ghost"
              size="icon"
              className="h-12 w-12 rounded-full text-slate-500 hover:text-white hover:bg-white/5"
            >
              <IconRefresh className="h-6 w-6" />
            </Button>

            <Button
              onClick={togglePlayPause}
              size="icon"
              className="h-24 w-24 rounded-full bg-white hover:bg-indigo-50 text-slate-950 transition-all hover:scale-105 active:scale-95 shadow-xl shadow-white/10"
            >
              {isPlaying ? (
                <IconPlayerPause className="h-10 w-10 fill-current" />
              ) : (
                <IconPlayerPlay className="h-10 w-10 fill-current ml-1" />
              )}
            </Button>

            <Button
              variant="ghost"
              size="icon"
              className="h-12 w-12 rounded-full text-slate-500"
            >
              <IconMusic className="h-6 w-6" />
            </Button>
          </div>
        </div>

        {/* Minimal Progress Bar (Bottom) */}
        <div className="fixed bottom-0 left-0 w-full h-1 bg-slate-900">
          <div 
            className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-1000 ease-linear"
            style={{ width: `${getProgressPercentage()}%` }}
          />
        </div>
      </div>
    </div>
  );
}
  // Exercise selection screen
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2 flex items-center justify-center gap-2">
          <IconBrain className="h-8 w-8 text-blue-500" />
          Guided Exercises
        </h1>
        <p className="text-muted-foreground">
          Choose an exercise to practice emotional intelligence skills
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {exercises.map((exercise) => (
          <Card key={exercise.id} className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <div className="flex items-start justify-between">
                <CardTitle className="text-lg">{exercise.title}</CardTitle>
                <Badge variant="secondary">{exercise.category}</Badge>
              </div>
              <CardDescription className="flex items-center gap-2">
                <IconClock className="h-4 w-4" />
                {Math.floor(exercise.duration / 60)} min • {exercise.description}
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">Exercise Steps:</h4>
                <ul className="text-sm space-y-1">
                  {exercise.steps.slice(0, 3).map((step, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      {step}
                    </li>
                  ))}
                  {exercise.steps.length > 3 && (
                    <li className="text-muted-foreground">+ {exercise.steps.length - 3} more steps</li>
                  )}
                </ul>
              </div>
              
              {['box-breathing', 'perspective-taking', 'gratitude-practice'].includes(exercise.id) ? (
                <Link href={`/exercise/${exercise.id}`}>
                  <Button className="w-full flex items-center gap-2">
                    <IconPlayerPlay className="h-4 w-4" />
                    Start Exercise
                  </Button>
                </Link>
              ) : (
                <Button 
                  onClick={() => startExercise(exercise)}
                  className="w-full flex items-center gap-2"
                >
                  <IconPlayerPlay className="h-4 w-4" />
                  Start Exercise
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}