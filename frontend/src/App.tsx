import { useState } from 'react';
import { Wand2, Loader2 } from 'lucide-react';

import { SplitPane } from './components/SplitPane';
import { ExcalidrawCanvas } from './components/ExcalidrawCanvas';
import { ProgressIndicator } from './components/ProgressIndicator';
import { useArchitectureStream } from './hooks/useArchitectureStream';

function App() {
  
  const streamState = useArchitectureStream();
  const [userInput, setUserInput] = useState('');

  const {status, currentNode, completedNodes, diagram, error, startGeneration} = streamState;
  const isGenerating = status === 'streaming';

  const handleGenerate = () => {

    //If input is too vague
    if(userInput.trim().length < 10) {
      alert("Provide a more detailed description(at least 10 characters).");
      return;
    }
    startGeneration(userInput);
  }

  const LeftPanel = () => (
    <div className="p-6 h-full flex flex-col">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Wand2 className="w-6 h-6 text-primary" />
              Architecture Agent
            </h1>
            <p className="text-zinc-400 text-sm mt-2">
              Describe your software system in plain English. Our AI multi-agent pipeline will generate a structured, styled architecture diagram.
            </p>
          </div>

          <ProgressIndicator
              status= {status}
              currentNode={currentNode}
              completedNodes={completedNodes}
              error={error}
          />
          
          <textarea 
            className="flex-1 w-full bg-zinc-900 border border-border rounded-lg p-4 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-primary resize-none transition-all"
            placeholder="e.g., A microservices architecture with a React frontend, Node.js API gateway, Python user service, Redis cache, and PostgreSQL database..."
            value = {userInput}
            onChange = {(e) => setUserInput(e.target.value)}
            disabled= {isGenerating}
          />
          
          <button 
              className="mt-4 w-full bg-primary hover:bg-primary-hover text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
              onClick={handleGenerate}
              disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <Loader2 className='w-4 h-4 animate-spin' />
                Generating...
              </>
            ) : (
              <>
                <Wand2 className="w-4 h-4" />
                Generate Diagram
              </>
            )}
          </button>
    </div>
  );

  const RightPanel = () => (
    <div className="h-full w-full bg-background relative">
      <ExcalidrawCanvas diagram = {diagram} />
    </div>
  );

   return (
    <SplitPane 
        leftPanel  = {<LeftPanel/>}
        rightPanel = {<RightPanel/>}
    />
   );
}

export default App;