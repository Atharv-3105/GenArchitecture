import { useState } from 'react';
import { SplitPane } from './components/SplitPane';
import { ExcalidrawCanvas } from './components/ExcalidrawCanvas';
import { ProgressIndicator } from './components/ProgressIndicator';
import { useArchitectureStream } from './hooks/useArchitectureStream';
import { Wand2, Loader2, Sparkles, FileText, X} from 'lucide-react';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';
import ReactMarkdown from 'react-markdown';



//Function which checks for SignedIn our SignedOut user
function App() {
  return (
    <div className="h-screen w-screen flex flex-col bg-background">
      {/* Header with Auth Buttons */}
      <header className="h-14 border-b border-border flex items-center justify-between px-6 flex-shrink-0">
        <h1 className="text-x1 font-bold text-white flex items-center gap-2">
          <Wand2 className="w-5 h-5 text-primary" />
            ArchiGen AI
        </h1>
        <nav className="flex items-center gap-4">
          <SignedOut>
            <SignInButton mode = "modal">
              <button className="bg-primary hover:bg-primary-hover text-white text-sm font-semibold py-2 px-4 rounded-md transition-colors">
                Sign In
              </button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <UserButton afterSignOutUrl='/' />
          </SignedIn>
        </nav>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden">
        <SignedIn>
           <AppContent />
        </SignedIn>
        <SignedOut>
          <div className="h-full flex flex-col items-center justify-center text-center p-8 bg-gradient-to-b from-background to-surface">
            <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-6">
              <Wand2 className="w-10 h-10 text-primary" />
            </div>
            <h2 className="text-4xl font-bold text-white mb-4">AgenticAI Architecture Diagrams</h2>
            <p className="text-zinc-400 mb-8 max-w-lg text-lg">
              Describe your software system in plain English.Our multi-agent AI system will generate a beautiful, structured Excalidraw diagram in seconds.
            </p>
            <SignInButton mode = "modal">
              <button className="bg-primary hover:bg-primary-hover text-white font-semibold py-3 px-8 rounded-lg transition-colors text-lg shadow-lg shadow-primary/20">
                Get Started for Free
              </button>
            </SignInButton>
            <p className="text-zinc-500 text-sm mt-6">5 free diagrams per day.</p>
          </div>
        </SignedOut>
      </main>
    </div>
  );
}

//The main app logic, which will only render if SignedIn
function AppContent() {
  const streamState = useArchitectureStream();
  const [userInput, setUserInput] = useState('');
  const [showADR, setShowADR] = useState(false);
  
  const { status, currentNode, completedNodes, diagram, error, startGeneration } = streamState;
  const isGenerating = status === 'streaming';

  const handleSubmit = () => {
    const minLen = diagram ? 5 : 10;
    if (userInput.trim().length < minLen) {
      alert(`Please provide at least ${minLen} characters.`);
      return;
    }
    startGeneration(userInput, diagram || undefined);
    setUserInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
  <div className='flex h-full w-full relative'>
    <SplitPane 
      leftPanel={
        // FIX: Inlined JSX prevents the component from unmounting on every keystroke
        <div className="p-6 h-full flex flex-col">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Wand2 className="w-6 h-6 text-primary" />
              ArchiGen AI
            </h1>
            <p className="text-zinc-400 text-sm mt-2">
              {diagram 
                ? "Diagram generated. Refine it with natural language." 
                : "Describe your software system in plain English."}
            </p>
          </div>
          
          <ProgressIndicator 
            status={status} 
            currentNode={currentNode} 
            completedNodes={completedNodes} 
            error={error} 
          />
          
          <div className="flex-1 flex flex-col">
            {diagram && !isGenerating ? (
              <div className="relative flex-1 flex flex-col">
                <div className="absolute top-3 left-4 text-zinc-500 text-xs font-semibold uppercase tracking-wider">
                  Refine Diagram
                </div>
                <textarea 
                  className="flex-1 w-full bg-zinc-900 border border-primary/50 rounded-lg pt-10 pb-14 px-4 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-primary resize-none transition-all"
                  placeholder="e.g., Add a Redis cache between the API and the DB..."
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                />
                <button 
                  className="absolute bottom-4 right-4 bg-primary hover:bg-primary-hover text-white font-semibold py-2 px-4 rounded-md transition-colors flex items-center gap-2 disabled:bg-zinc-700 disabled:cursor-not-allowed"
                  onClick={handleSubmit}
                  disabled={isGenerating}
                >
                  <Sparkles className="w-4 h-4" />
                  Refine
                </button>
              </div>
            ) : (
              <textarea 
                className="flex-1 w-full bg-zinc-900 border border-border rounded-lg p-4 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-primary resize-none transition-all"
                placeholder="e.g., A microservices architecture with a React frontend, Node.js API gateway, Python user service, Redis cache, and PostgreSQL database..."
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isGenerating}
              />
            )}
          </div>
          
          {!diagram && (
            <button 
              className="mt-4 w-full bg-primary hover:bg-primary-hover disabled:bg-zinc-700 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
              onClick={handleSubmit}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Wand2 className="w-4 h-4" />
                  Generate Diagram
                </>
              )}
            </button>
          )}
          {diagram?.adr_markdown && (
              <button 
                  onClick = {() => setShowADR(true)}
                  className = "mt-4 w-full bg-surface hover:bg-zinc-800 border border-border text-zinc-300 font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <FileText className = "w-4 h-4" />
                View Architecture Decision Record 
              </button>
            )}
        </div>
      }
      rightPanel={
        <div className="h-full w-full bg-background relative">
          <ExcalidrawCanvas diagram={diagram} />
        </div>
      }
    />

    {showADR && diagram?.adr_markdown && (
      <div className='absolute inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-8'>
        <div className="bg-surface border border-border rounded-xl shadow-2xl w-full max-w-3xl max-h-[80vh] flex flex-col overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-border">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary" />
                Architecture Decision Record
              </h2>
              <button onClick={() => setShowADR(false)} className="text-zinc-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto prose prose-invert max-w-none">
              <ReactMarkdown>{diagram.adr_markdown}</ReactMarkdown>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;