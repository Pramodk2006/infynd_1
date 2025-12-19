import React from 'react';
import { Link } from 'react-router-dom';
import { Database, Zap, Search, ArrowRight, BarChart3, FileText, Layers, ShieldCheck } from 'lucide-react';

const LandingPage = () => {
    return (
        <div className="min-h-screen bg-slate-50 dark:bg-infynd-dark text-slate-900 dark:text-white transition-colors duration-300">

            {/* Hero Section */}
            <section className="relative pt-20 pb-32 overflow-hidden">
                <div className="container mx-auto px-6 relative z-10">
                    <div className="max-w-4xl mx-auto text-center">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 text-sm font-semibold mb-6 animate-fade-in">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
                            </span>
                            Next Gen Data Processing
                        </div>

                        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 leading-tight animate-fade-in-up">
                            Data <span className="text-primary-600 dark:text-primary-400">Fusion</span> Engine
                        </h1>

                        <p className="text-xl text-slate-600 dark:text-slate-300 mb-10 max-w-2xl mx-auto leading-relaxed animate-fade-in-up delay-100">
                            Transform raw data into actionable intelligence. Extract, classify, and analyze company information from any source with AI-powered precision.
                        </p>

                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up delay-200">
                            <Link to="/dashboard" className="px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-bold text-lg shadow-lg hover:shadow-primary-500/30 transition-all flex items-center gap-2 transform hover:-translate-y-1">
                                Get Started <ArrowRight size={20} />
                            </Link>
                            <a href="#features" className="px-8 py-4 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl font-bold text-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-all">
                                Learn More
                            </a>
                        </div>
                    </div>
                </div>

                {/* Abstract Background Shapes */}
                <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                    <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary-500/5 rounded-full blur-3xl -mr-32 -mt-32"></div>
                    <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-3xl -ml-32 -mb-32"></div>
                </div>
            </section>

            {/* Features Grid (Bento Style) */}
            <section id="features" className="py-20 bg-white dark:bg-slate-900/50">
                <div className="container mx-auto px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-4xl font-bold mb-4">Powerful Capabilities</h2>
                        <p className="text-lg text-slate-600 dark:text-slate-400">Everything you need to master your B2B data pipeline</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">

                        {/* Feature 1: Extraction - Large Card */}
                        <div className="md:col-span-2 bg-slate-50 dark:bg-infynd-card-dark rounded-2xl p-8 shadow-bento hover:shadow-bento-hover transition-all border border-slate-100 dark:border-slate-800 relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity transform group-hover:scale-110 duration-500">
                                <Database size={200} />
                            </div>
                            <div className="relative z-10">
                                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center text-blue-600 dark:text-blue-400 mb-6">
                                    <Database size={24} />
                                </div>
                                <h3 className="text-2xl font-bold mb-3">Multi-Source Extraction</h3>
                                <p className="text-slate-600 dark:text-slate-400 mb-6 max-w-md">
                                    Ingest data seamlessly from URLs, PDFs, HTML files, or raw text. Our intelligent crawlers handle complex website structures to retrieve the data that matters.
                                </p>
                                <div className="flex gap-2">
                                    <span className="px-3 py-1 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-lg text-xs font-semibold">Web Crawling</span>
                                    <span className="px-3 py-1 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-lg text-xs font-semibold">PDF Parsing</span>
                                </div>
                            </div>
                        </div>

                        {/* Feature 2: Classification */}
                        <div className="bg-slate-50 dark:bg-infynd-card-dark rounded-2xl p-8 shadow-bento hover:shadow-bento-hover transition-all border border-slate-100 dark:border-slate-800">
                            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center text-purple-600 dark:text-purple-400 mb-6">
                                <Layers size={24} />
                            </div>
                            <h3 className="text-xl font-bold mb-3">AI Classification</h3>
                            <p className="text-slate-600 dark:text-slate-400 text-sm">
                                Automatically categorize companies into precise sectors and industries using advanced LLMs and embedding models.
                            </p>
                        </div>

                        {/* Feature 3: Analysis */}
                        <div className="bg-slate-50 dark:bg-infynd-card-dark rounded-2xl p-8 shadow-bento hover:shadow-bento-hover transition-all border border-slate-100 dark:border-slate-800">
                            <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-900/30 rounded-xl flex items-center justify-center text-emerald-600 dark:text-emerald-400 mb-6">
                                <BarChart3 size={24} />
                            </div>
                            <h3 className="text-xl font-bold mb-3">Deep Analysis</h3>
                            <p className="text-slate-600 dark:text-slate-400 text-sm">
                                Generate executive summaries, extract key personnel, and identify technologies used, all in seconds.
                            </p>
                        </div>

                        {/* Feature 4: Batch Processing - Large Card */}
                        <div className="md:col-span-2 bg-slate-50 dark:bg-infynd-card-dark rounded-2xl p-8 shadow-bento hover:shadow-bento-hover transition-all border border-slate-100 dark:border-slate-800 relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity transform group-hover:scale-110 duration-500">
                                <Zap size={200} />
                            </div>
                            <div className="relative z-10">
                                <div className="w-12 h-12 bg-amber-100 dark:bg-amber-900/30 rounded-xl flex items-center justify-center text-amber-600 dark:text-amber-400 mb-6">
                                    <Zap size={24} />
                                </div>
                                <h3 className="text-2xl font-bold mb-3">Batch Processing at Scale</h3>
                                <p className="text-slate-600 dark:text-slate-400 mb-6 max-w-md">
                                    Process hundreds of sources simultaneously. Our resilient batch engine handles errors gracefully and ensures your data pipeline never stops.
                                </p>
                                <div className="flex gap-2">
                                    <span className="px-3 py-1 bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 rounded-lg text-xs font-semibold">High Concurrency</span>
                                    <span className="px-3 py-1 bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 rounded-lg text-xs font-semibold">Fault Tolerant</span>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-12">
                <div className="container mx-auto px-6 text-center">
                    <div className="flex items-center justify-center gap-2 mb-4 text-slate-900 dark:text-white font-bold text-xl">
                        <div className="bg-primary-600 p-1.5 rounded-lg">
                            <BarChart3 size={20} className="text-white" />
                        </div>
                        Data Fusion Engine
                    </div>
                    <p className="text-slate-500 dark:text-slate-400">© 2024 Data Fusion Engine. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
