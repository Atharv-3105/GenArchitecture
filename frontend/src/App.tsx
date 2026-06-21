import { useState } from 'react';
import { SplitPane } from './components/SplitPane';
import { ExcalidrawCanvas } from './components/ExcalidrawCanvas';
import { ProgressIndicator } from './components/ProgressIndicator';
import { useArchitectureStream } from './hooks/useArchitectureStream';
import { Wand2, Loader2, Sparkles } from 'lucide-react';

function App() {
  const streamState = useArchitectureStream();
  const [userInput, setUserInput] = useState('');
  
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
        </div>
      }
      rightPanel={
        <div className="h-full w-full bg-background relative">
          <ExcalidrawCanvas diagram={diagram} />
        </div>
      }
    />
  );
}

export default App;