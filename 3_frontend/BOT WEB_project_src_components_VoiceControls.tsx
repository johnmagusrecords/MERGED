import React, { useEffect, useState } from 'react';
import { Mic, MicOff, Volume2 } from 'lucide-react';
import { useSpeechRecognition } from 'react-speech-recognition';
import { VoiceCommandManager } from '../services/VoiceCommandManager';
import { useTradingBot } from '../hooks/useTradingBot';

export default function VoiceControls() {
  const [isListening, setIsListening] = useState(false);
  const [lastCommand, setLastCommand] = useState<string>('');
  const { bot } = useTradingBot();
  const voiceManager = new VoiceCommandManager(bot);
  
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition
  } = useSpeechRecognition();

  useEffect(() => {
    if (transcript) {
      const commandExecuted = voiceManager.handleCommand(transcript);
      if (commandExecuted) {
        setLastCommand(transcript);
        resetTranscript();
      }
    }
  }, [transcript]);

  const toggleListening = () => {
    if (isListening) {
      voiceManager.stopListening();
    } else {
      voiceManager.startListening();
    }
    setIsListening(!isListening);
  };

  if (!browserSupportsSpeechRecognition) {
    return (
      <div className="text-red-500 text-sm">
        Browser doesn't support voice commands
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Voice Controls</h3>
        <button
          onClick={toggleListening}
          className={`p-2 rounded-full ${
            isListening ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'
          }`}
        >
          {isListening ? <Mic className="h-5 w-5" /> : <MicOff className="h-5 w-5" />}
        </button>
      </div>

      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <Volume2 className="h-4 w-4 text-gray-500" />
          <span className="text-sm text-gray-600">
            {isListening ? 'Listening...' : 'Voice commands inactive'}
          </span>
        </div>

        {lastCommand && (
          <div className="text-sm">
            <span className="font-medium">Last command:</span>
            <span className="ml-2 text-gray-600">{lastCommand}</span>
          </div>
        )}

        <div className="text-xs text-gray-500">
          <p className="font-medium mb-1">Available commands:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>"Start bot"</li>
            <li>"Stop bot"</li>
            <li>"Switch to safe mode"</li>
            <li>"Switch to recovery mode"</li>
            <li>"Close all positions"</li>
            <li>"Show performance"</li>
          </ul>
        </div>
      </div>
    </div>
  );
}