"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Calendar } from "@/components/ui/calendar";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { IconCalendar, IconClock, IconUser, IconPhone, IconArrowUpRight } from "@tabler/icons-react";
import { Separator } from "@/components/ui/separator";
import { format } from "date-fns";

export default function PsychologistConsultation() {
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined);
  const [selectedTime, setSelectedTime] = useState<string>("");
  const [fullName, setFullName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [phoneNumber, setPhoneNumber] = useState<string>("");
  const [concern, setConcern] = useState<string>("");
  const [submitted, setSubmitted] = useState(false);
  const [timeZone, setTimeZone] = useState("UTC-5 (EST)");
  const [isDateTimeModalOpen, setIsDateTimeModalOpen] = useState(false);
  const [tempDate, setTempDate] = useState<Date | undefined>(undefined);
  const [tempTime, setTempTime] = useState<string>("");

  // Generate available time slots (9 AM to 5 PM in 1-hour intervals)
  const timeSlots = [
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!selectedDate || !selectedTime || !fullName || !email || !phoneNumber) {
      alert("Please fill in all required fields");
      return;
    }

    // Format the appointment details
    const appointmentData = {
      fullName,
      email,
      phoneNumber,
      date: format(selectedDate, "yyyy-MM-dd"),
      time: selectedTime,
      timeZone,
      concern,
      bookedAt: new Date().toISOString(),
    };

    try {
      // Call API endpoint to book appointment
      const response = await fetch("/api/psychologist-consultation", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(appointmentData),
      });

      if (response.ok) {
        setSubmitted(true);
        // Reset form after 3 seconds
        setTimeout(() => {
          setFullName("");
          setEmail("");
          setPhoneNumber("");
          setSelectedDate(undefined);
          setSelectedTime("");
          setConcern("");
          setSubmitted(false);
        }, 3000);
      } else {
        alert("Failed to book appointment. Please try again.");
      }
    } catch (error) {
      console.error("Error booking appointment:", error);
      alert("An error occurred. Please try again.");
    }
  };

  const getDayOfWeek = (date: Date | undefined) => {
    if (!date) return "";
    return format(date, "EEEE, MMMM d");
  };

  const formatTimeDisplay = (time: string) => {
    if (!time) return "";
    const hour = parseInt(time.split(":")[0]);
    const displayHour = hour === 0 ? "12" : hour > 12 ? hour - 12 : hour;
    const ampm = hour >= 12 ? "PM" : "AM";
    return `${displayHour}:${time.split(":")[1]}${ampm}`;
  };

  const formattedDate = selectedDate
    ? format(selectedDate, "EEEE, MMMM d, yyyy")
    : "Not selected";

  const formattedTime = selectedTime
    ? formatTimeDisplay(selectedTime)
    : "Not selected";

  const handleOpenModal = () => {
    setTempDate(selectedDate);
    setTempTime(selectedTime);
    setIsDateTimeModalOpen(true);
  };

  const handleConfirmDateTime = () => {
    if (tempDate && tempTime) {
      setSelectedDate(tempDate);
      setSelectedTime(tempTime);
      setIsDateTimeModalOpen(false);
    }
  };

  const handleCancelDateTime = () => {
    setTempDate(undefined);
    setTempTime("");
    setIsDateTimeModalOpen(false);
  };

  return (
    <div className="relative isolate flex flex-1 flex-col overflow-hidden bg-gradient-to-b from-slate-50 via-white to-white dark:from-slate-950 dark:via-slate-950 dark:to-slate-900">
      <div className="pointer-events-none absolute inset-x-0 top-[-10%] h-64 bg-gradient-to-r from-purple-200/40 via-pink-200/30 to-rose-200/30 blur-3xl dark:from-purple-500/10 dark:via-pink-400/5 dark:to-rose-400/10" />

      <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col px-4 pb-12 pt-8 lg:px-8 lg:pt-10">
        {/* Header */}
        <div className="mb-8">
          <Badge
            variant="outline"
            className="mb-3 w-fit border-purple-300/30 bg-purple-50/50 text-purple-700 dark:border-purple-400/40 dark:bg-purple-500/10 dark:text-purple-200"
          >
            <IconUser className="mr-1.5 size-4" />
            Professional Support
          </Badge>
          <h1 className="text-balance text-3xl font-semibold leading-tight tracking-tight text-slate-900 dark:text-slate-50 lg:text-4xl">
            Book a Session with a Psychologist
          </h1>
          <p className="mt-2 max-w-2xl text-base text-muted-foreground">
            Connect with licensed mental health professionals who are ready to listen and help you
            work through your challenges.
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          {/* Form Section */}
          <div className="lg:col-span-2">
            <Card className="relative overflow-hidden border-purple-200/30 shadow-lg dark:border-purple-400/20">
              <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-purple-50/40 via-transparent to-pink-100/20 dark:from-purple-500/5 dark:via-transparent dark:to-pink-400/5" />
              <CardHeader className="relative">
                <CardTitle>Schedule Your Appointment</CardTitle>
                <CardDescription>
                  Select your preferred date and time, then tell us about your concerns
                </CardDescription>
              </CardHeader>

              {submitted ? (
                <CardContent className="relative">
                  <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-6 text-center dark:border-emerald-400/20 dark:bg-emerald-500/10">
                    <h3 className="text-lg font-semibold text-emerald-900 dark:text-emerald-100">
                      ✓ Appointment Booked Successfully!
                    </h3>
                    <p className="mt-2 text-sm text-emerald-700 dark:text-emerald-200">
                      A confirmation email has been sent to <strong>{email}</strong>. Our psychologist will
                      contact you shortly.
                    </p>
                  </div>
                </CardContent>
              ) : (
                <CardContent className="relative">
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Personal Information */}
                    <div className="space-y-4">
                      <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                        Personal Information
                      </h3>
                      <div className="grid gap-4 sm:grid-cols-2">
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                            Full Name *
                          </label>
                          <Input
                            placeholder="Enter your full name"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            className="border-slate-200 dark:border-slate-700"
                          />
                        </div>
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                            Email Address *
                          </label>
                          <Input
                            type="email"
                            placeholder="your.email@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="border-slate-200 dark:border-slate-700"
                          />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                          <IconPhone className="mr-1.5 inline size-4" />
                          Phone Number *
                        </label>
                        <Input
                          type="tel"
                          placeholder="+1 (555) 000-0000"
                          value={phoneNumber}
                          onChange={(e) => setPhoneNumber(e.target.value)}
                          className="border-slate-200 dark:border-slate-700"
                        />
                      </div>
                    </div>

                    <Separator />

                    {/* Date and Time Selection - Modal Trigger */}
                    <div className="space-y-4">
                      <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                        <IconCalendar className="mr-2 inline size-4" />
                        Select a Date & Time
                      </h3>
                      
                      <div className="grid gap-4 sm:grid-cols-2">
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                            Selected Date *
                          </label>
                          <Button
                            type="button"
                            variant="outline"
                            onClick={handleOpenModal}
                            className="w-full justify-start text-left font-normal border-slate-200 dark:border-slate-700"
                          >
                            <IconCalendar className="mr-2 h-4 w-4" />
                            {selectedDate ? format(selectedDate, "PPP") : "Pick a date"}
                          </Button>
                        </div>
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                            Selected Time *
                          </label>
                          <Button
                            type="button"
                            variant="outline"
                            onClick={handleOpenModal}
                            className="w-full justify-start text-left font-normal border-slate-200 dark:border-slate-700"
                          >
                            <IconClock className="mr-2 h-4 w-4" />
                            {selectedTime ? formatTimeDisplay(selectedTime) : "Pick a time"}
                          </Button>
                        </div>
                      </div>

                      {/* Time Zone */}
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                          Time Zone
                        </label>
                        <select
                          value={timeZone}
                          onChange={(e) => setTimeZone(e.target.value)}
                          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-300"
                        >
                          <option value="UTC-8 (PST)">UTC-8 (PST)</option>
                          <option value="UTC-7 (MST)">UTC-7 (MST)</option>
                          <option value="UTC-6 (CST)">UTC-6 (CST)</option>
                          <option value="UTC-5 (EST)">UTC-5 (EST)</option>
                          <option value="UTC (GMT)">UTC (GMT)</option>
                          <option value="UTC+1 (CET)">UTC+1 (CET)</option>
                          <option value="UTC+5:30 (IST)">UTC+5:30 (IST)</option>
                        </select>
                      </div>
                    </div>

                    <Separator />

                    {/* Concerns */}
                    <div className="space-y-4">
                      <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                        Your Concerns
                      </h3>
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                          What would you like to discuss? (Optional)
                        </label>
                        <Textarea
                          placeholder="Share any specific concerns or topics you'd like to discuss with your psychologist..."
                          value={concern}
                          onChange={(e) => setConcern(e.target.value)}
                          className="min-h-32 border-slate-200 dark:border-slate-700"
                        />
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          This helps us match you with the most suitable psychologist.
                        </p>
                      </div>
                    </div>

                    {/* Submit Button */}
                    <Button
                      type="submit"
                      size="lg"
                      className="w-full bg-gradient-to-r from-purple-600 to-pink-600 shadow-lg shadow-purple-500/20 hover:from-purple-700 hover:to-pink-700"
                    >
                      Book Appointment
                      <IconArrowUpRight className="ml-2 size-4" />
                    </Button>
                  </form>
                </CardContent>
              )}
            </Card>
          </div>

          {/* Sidebar - Appointment Summary & Benefits */}
          <div className="space-y-6">
            {/* Appointment Summary */}
            <Card className="relative overflow-hidden border-slate-200/50 dark:border-slate-700/50">
              <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-slate-50/40 via-transparent to-slate-100/20 dark:from-slate-800/40 dark:via-transparent dark:to-slate-700/20" />
              <CardHeader className="relative">
                <CardTitle className="text-lg">Your Selection</CardTitle>
              </CardHeader>
              <CardContent className="relative space-y-4">
                <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-4 dark:border-slate-700 dark:bg-slate-800/30">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                    Selected Date
                  </p>
                  <p className="mt-1 text-sm font-medium text-slate-900 dark:text-slate-100">
                    {formattedDate}
                  </p>
                </div>
                <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-4 dark:border-slate-700 dark:bg-slate-800/30">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                    Selected Time
                  </p>
                  <p className="mt-1 text-sm font-medium text-slate-900 dark:text-slate-100">
                    {formattedTime}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Benefits */}
            <Card className="relative overflow-hidden border-emerald-200/30 dark:border-emerald-400/20">
              <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-emerald-50/40 via-transparent to-emerald-100/20 dark:from-emerald-500/5 dark:via-transparent dark:to-emerald-400/5" />
              <CardHeader className="relative">
                <CardTitle className="text-lg">Why Talk to a Psychologist?</CardTitle>
              </CardHeader>
              <CardContent className="relative">
                <ul className="space-y-3 text-sm text-slate-700 dark:text-slate-300">
                  <li className="flex gap-3">
                    <span className="text-emerald-600 dark:text-emerald-400">✓</span>
                    <span>Licensed, certified professionals with years of experience</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-emerald-600 dark:text-emerald-400">✓</span>
                    <span>Personalized treatment plans tailored to your needs</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-emerald-600 dark:text-emerald-400">✓</span>
                    <span>Confidential and secure sessions</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-emerald-600 dark:text-emerald-400">✓</span>
                    <span>Evidence-based therapeutic techniques</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-emerald-600 dark:text-emerald-400">✓</span>
                    <span>Flexible scheduling for your convenience</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Date & Time Selection Modal */}
      <Dialog open={isDateTimeModalOpen} onOpenChange={setIsDateTimeModalOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl">Select Date & Time</DialogTitle>
            <DialogDescription>
              Choose your preferred appointment date and time slot
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-6 lg:grid-cols-2 py-4">
            {/* Calendar Section */}
            <div className="flex flex-col items-center">
              <div className="w-full rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-950">
                <Calendar
                  mode="single"
                  selected={tempDate}
                  onSelect={setTempDate}
                  disabled={(date) =>
                    date < new Date(new Date().setHours(0, 0, 0, 0))
                  }
                  className="w-full"
                />
              </div>
            </div>

            {/* Time Selection */}
            <div className="flex flex-col">
              {/* Selected Date Display */}
              {tempDate && (
                <div className="mb-6 rounded-lg bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 p-4 text-center">
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-300">Selected Date</p>
                  <p className="mt-2 text-lg font-bold text-blue-700 dark:text-blue-300">
                    {getDayOfWeek(tempDate)}
                  </p>
                </div>
              )}

              {/* Time Slots */}
              <div className="flex-1">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3 block">
                  <IconClock className="mr-1.5 inline size-4" />
                  Available Times
                </label>
                <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2">
                  {timeSlots.map((time) => (
                    <button
                      key={time}
                      type="button"
                      onClick={() => setTempTime(time)}
                      className={`w-full flex items-center justify-between rounded-lg px-4 py-3 text-sm font-medium transition-all ${
                        tempTime === time
                          ? "bg-blue-600 text-white shadow-lg shadow-blue-500/30"
                          : "border border-slate-300 bg-white text-slate-700 hover:border-blue-400 hover:bg-blue-50 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-blue-500 dark:hover:bg-slate-800"
                      }`}
                    >
                      <span>{formatTimeDisplay(time)}</span>
                      {tempTime === time && (
                        <span className="text-xs font-semibold bg-blue-700 px-2 py-1 rounded">
                          Selected
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <DialogFooter className="gap-2 sm:gap-0">
            <Button
              type="button"
              variant="outline"
              onClick={handleCancelDateTime}
            >
              Cancel
            </Button>
            <Button
              type="button"
              onClick={handleConfirmDateTime}
              disabled={!tempDate || !tempTime}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            >
              Confirm Selection
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
