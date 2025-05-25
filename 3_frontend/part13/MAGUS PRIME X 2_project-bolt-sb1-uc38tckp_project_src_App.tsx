import React from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { 
  TrendingUp, 
  BookOpen, 
  Shield, 
  Globe2, 
  LineChart as ChartLineUp,
  Wallet,
  Award,
  ArrowRight
} from 'lucide-react';

// Pages
const Markets = () => (
  <div className="container mx-auto px-6 py-12">
    <h1 className="text-3xl font-bold mb-8">Markets Overview</h1>
    {/* Add markets content */}
  </div>
);

const Trading = () => (
  <div className="container mx-auto px-6 py-12">
    <h1 className="text-3xl font-bold mb-8">Trading Platform</h1>
    {/* Add trading content */}
  </div>
);

const Learn = () => (
  <div className="container mx-auto px-6 py-12">
    <h1 className="text-3xl font-bold mb-8">Learning Center</h1>
    {/* Add learning content */}
  </div>
);

const About = () => (
  <div className="container mx-auto px-6 py-12">
    <h1 className="text-3xl font-bold mb-8">About Magus Prime X</h1>
    {/* Add about content */}
  </div>
);

const SignIn = () => {
  const navigate = useNavigate();
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Add authentication logic here
    navigate('/trading');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6">Sign In to Magus Prime X</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 mb-2" htmlFor="email">
              Email
            </label>
            <input
              type="email"
              id="email"
              className="w-full p-2 border rounded-lg"
              required
            />
          </div>
          <div className="mb-6">
            <label className="block text-gray-700 mb-2" htmlFor="password">
              Password
            </label>
            <input
              type="password"
              id="password"
              className="w-full p-2 border rounded-lg"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
};

const Register = () => {
  const navigate = useNavigate();
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Add registration logic here
    navigate('/trading');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6">Create Your Account</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 mb-2" htmlFor="name">
              Full Name
            </label>
            <input
              type="text"
              id="name"
              className="w-full p-2 border rounded-lg"
              required
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 mb-2" htmlFor="email">
              Email
            </label>
            <input
              type="email"
              id="email"
              className="w-full p-2 border rounded-lg"
              required
            />
          </div>
          <div className="mb-6">
            <label className="block text-gray-700 mb-2" htmlFor="password">
              Password
            </label>
            <input
              type="password"
              id="password"
              className="w-full p-2 border rounded-lg"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Create Account
          </button>
        </form>
      </div>
    </div>
  );
};

const HomePage = () => (
  <>
    {/* Hero Section */}
    <header className="bg-gradient-to-r from-blue-900 to-blue-800 text-white">
      <div className="container mx-auto px-6 py-20">
        <div className="flex flex-col md:flex-row items-center">
          <div className="md:w-1/2 mb-10 md:mb-0">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Master the Markets with Magus Prime X
            </h1>
            <p className="text-xl mb-8 text-blue-100">
              Access global markets with advanced trading tools and professional insights.
            </p>
            <Link
              to="/register"
              className="bg-blue-500 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-600 transition flex items-center inline-flex"
            >
              Start Trading <ArrowRight className="ml-2" />
            </Link>
          </div>
          <div className="md:w-1/2">
            <img 
              src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=2000&q=80" 
              alt="Trading Platform" 
              className="rounded-lg shadow-2xl"
            />
          </div>
        </div>
      </div>
    </header>

    {/* Features Section */}
    <section className="py-20 container mx-auto px-6">
      <h2 className="text-3xl font-bold text-center mb-16">Why Choose Magus Prime X</h2>
      <div className="grid md:grid-cols-3 gap-12">
        <div className="text-center">
          <div className="bg-blue-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-6">
            <Globe2 className="h-8 w-8 text-blue-900" />
          </div>
          <h3 className="text-xl font-semibold mb-4">Global Markets</h3>
          <p className="text-gray-600">Access thousands of instruments across forex, stocks, crypto, and commodities</p>
        </div>
        <div className="text-center">
          <div className="bg-blue-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-6">
            <ChartLineUp className="h-8 w-8 text-blue-900" />
          </div>
          <h3 className="text-xl font-semibold mb-4">Advanced Analytics</h3>
          <p className="text-gray-600">Professional-grade charts and technical analysis tools</p>
        </div>
        <div className="text-center">
          <div className="bg-blue-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-6">
            <Shield className="h-8 w-8 text-blue-900" />
          </div>
          <h3 className="text-xl font-semibold mb-4">Secure Trading</h3>
          <p className="text-gray-600">Bank-grade security and regulated trading environment</p>
        </div>
      </div>
    </section>

    {/* Market Overview */}
    <section className="bg-white py-20">
      <div className="container mx-auto px-6">
        <h2 className="text-3xl font-bold text-center mb-16">Popular Markets</h2>
        <div className="grid md:grid-cols-4 gap-6">
          {[
            { name: 'EUR/USD', price: '1.0921', change: '+0.15%' },
            { name: 'Bitcoin', price: '52,341.00', change: '-1.23%' },
            { name: 'Gold', price: '2,031.50', change: '+0.45%' },
            { name: 'Tesla', price: '187.89', change: '+2.34%' }
          ].map((market) => (
            <div key={market.name} className="bg-slate-50 p-6 rounded-lg hover:shadow-lg transition">
              <h3 className="font-semibold mb-2">{market.name}</h3>
              <p className="text-2xl mb-1">${market.price}</p>
              <p className={market.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}>
                {market.change}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* CTA Section */}
    <section className="bg-blue-900 text-white py-20">
      <div className="container mx-auto px-6 text-center">
        <h2 className="text-3xl font-bold mb-8">Ready to Start Trading?</h2>
        <p className="text-xl mb-8 text-blue-100">Join millions of traders worldwide</p>
        <Link
          to="/register"
          className="bg-white text-blue-900 px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-50 transition inline-block"
        >
          Create Free Account
        </Link>
      </div>
    </section>
  </>
);

function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-gradient-to-r from-blue-900 to-blue-800 text-white">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center space-x-2">
            <TrendingUp className="h-8 w-8" />
            <span className="text-xl font-bold">Magus Prime X</span>
          </Link>
          <div className="hidden md:flex space-x-8">
            <Link to="/markets" className="hover:text-blue-200">Markets</Link>
            <Link to="/trading" className="hover:text-blue-200">Trading</Link>
            <Link to="/learn" className="hover:text-blue-200">Learn</Link>
            <Link to="/about" className="hover:text-blue-200">About</Link>
          </div>
          <div className="space-x-4">
            <Link
              to="/signin"
              className="px-4 py-2 text-blue-900 bg-white rounded-lg hover:bg-blue-50 transition"
            >
              Sign In
            </Link>
          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/markets" element={<Markets />} />
        <Route path="/trading" element={<Trading />} />
        <Route path="/learn" element={<Learn />} />
        <Route path="/about" element={<About />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/register" element={<Register />} />
      </Routes>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <Link to="/" className="flex items-center space-x-2 mb-6">
                <TrendingUp className="h-6 w-6" />
                <span className="text-lg font-bold">Magus Prime X</span>
              </Link>
              <p className="text-slate-400">Your trusted trading partner</p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Products</h4>
              <ul className="space-y-2 text-slate-400">
                <li><Link to="/markets" className="hover:text-white">Forex</Link></li>
                <li><Link to="/markets" className="hover:text-white">Stocks</Link></li>
                <li><Link to="/markets" className="hover:text-white">Cryptocurrencies</Link></li>
                <li><Link to="/markets" className="hover:text-white">Commodities</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Learn</h4>
              <ul className="space-y-2 text-slate-400">
                <li><Link to="/learn" className="hover:text-white">Trading Guides</Link></li>
                <li><Link to="/learn" className="hover:text-white">Market Analysis</Link></li>
                <li><Link to="/learn" className="hover:text-white">Education</Link></li>
                <li><Link to="/learn" className="hover:text-white">News</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-slate-400">
                <li><Link to="/about" className="hover:text-white">About Us</Link></li>
                <li><Link to="/about" className="hover:text-white">Contact</Link></li>
                <li><Link to="/about" className="hover:text-white">Legal</Link></li>
                <li><Link to="/about" className="hover:text-white">Privacy Policy</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 mt-12 pt-8 text-center text-slate-400">
            <p>© 2025 Magus Prime X. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;