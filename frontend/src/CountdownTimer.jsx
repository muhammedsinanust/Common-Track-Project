import React, { useState, useEffect } from 'react';

const CountdownTimer = ({ targetDate, onComplete }) => {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  });
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = new Date().getTime();
      const target = new Date(targetDate).getTime();
      const difference = target - now;

      if (difference <= 0) {
        setIsComplete(true);
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 });
        if (onComplete) onComplete();
        return;
      }

      setTimeLeft({
        days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((difference / 1000 / 60) % 60),
        seconds: Math.floor((difference / 1000) % 60),
      });
    };

    calculateTimeLeft();
    const timer = setInterval(calculateTimeLeft, 1000);

    return () => clearInterval(timer);
  }, [targetDate, onComplete]);

  if (isComplete) {
    return <span className="text-green-600 font-bold">LIVE NOW!</span>;
  }

  return (
    <div className="text-center">
      <div className="grid grid-cols-4 gap-2 text-sm">
        <div className="bg-gray-200 p-2 rounded">
          <div className="font-bold text-lg">{timeLeft.days}</div>
          <div className="text-xs">Days</div>
        </div>
        <div className="bg-gray-200 p-2 rounded">
          <div className="font-bold text-lg">{timeLeft.hours}</div>
          <div className="text-xs">Hours</div>
        </div>
        <div className="bg-gray-200 p-2 rounded">
          <div className="font-bold text-lg">{timeLeft.minutes}</div>
          <div className="text-xs">Mins</div>
        </div>
        <div className="bg-gray-200 p-2 rounded">
          <div className="font-bold text-lg">{timeLeft.seconds}</div>
          <div className="text-xs">Secs</div>
        </div>
      </div>
    </div>
  );
};

export default CountdownTimer;
