import React, { useState } from 'react';
import { ExternalLink } from 'lucide-react';

interface LogoProps {
  title: string;
  coloredLogo: string;
  transparentLogo: string;
  link?: string;
  description: string;
}

const Logo: React.FC<LogoProps> = ({ title, coloredLogo, transparentLogo, link, description }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div 
      className="flex flex-col items-center p-6 bg-white rounded-lg shadow-lg hover:shadow-xl transition-all"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="w-32 h-32 mb-4 relative">
        <img
          src={isHovered ? transparentLogo : coloredLogo}
          alt={title}
          className="w-full h-full object-contain transition-opacity duration-300"
        />
      </div>
      <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-center mb-4">{description}</p>
      {link && (
        <a 
          href={link} 
          target="_blank" 
          rel="noopener noreferrer"
          className="inline-flex items-center text-blue-600 hover:text-blue-800"
        >
          <span>Open Channel</span>
          <ExternalLink className="ml-1 h-4 w-4" />
        </a>
      )}
    </div>
  );
}

export default function LogoSection() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <Logo
        title="Prime X Signals"
        coloredLogo="/assets/logos/signals-colored.png"
        transparentLogo="/assets/logos/signals-transparent.png"
        link="https://t.me/PrimeXSignals"
        description="Join our Telegram channel for real-time trading signals"
      />
      <Logo
        title="Prime X News"
        coloredLogo="/assets/logos/news-colored.png"
        transparentLogo="/assets/logos/news-transparent.png"
        link="https://t.me/PrimeXNews"
        description="Stay updated with market news and analysis"
      />
      <Logo
        title="Magus Prime X Bot"
        coloredLogo="/assets/logos/bot-colored.png"
        transparentLogo="/assets/logos/bot-transparent.png"
        description="Powered by advanced AI trading algorithms"
      />
      <Logo
        title="Magus Prime X"
        coloredLogo="/assets/logos/app-colored.png"
        transparentLogo="/assets/logos/app-transparent.png"
        description="Professional trading platform"
      />
    </div>
  );
}