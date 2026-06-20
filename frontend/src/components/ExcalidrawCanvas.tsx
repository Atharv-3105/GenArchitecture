import { Excalidraw, MainMenu, WelcomeScreen } from '@excalidraw/excalidraw';
import { useEffect, useCallback, useState } from 'react';
import {type DiagramPayload } from '../lib/schema';

import "@excalidraw/excalidraw/index.css";

interface ExcalidrawCanvasProps {
  diagram: DiagramPayload | null;
}


export const ExcalidrawCanvas: React.FC<ExcalidrawCanvasProps> = ({ diagram }) => {
  const [excalidrawAPI, setExcalidrawAPI] = useState<any>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  const updateCanvas = useCallback((newDiagram: DiagramPayload) => {
    if(!excalidrawAPI) {
      console.warn('Excalidraw API not ready yet.');
      return;
    }

    console.log('Updating canvas with', newDiagram.elements.length, 'elements');

    //Use Excalidraw API to update the scene
    excalidrawAPI.updateScene({
      elements: newDiagram.elements as any,
      appState: {
        ...newDiagram.appState,
        viewBackgroundColor: newDiagram.appState?.viewBackgroundColor || '#09090b',
        theme: 'dark',
      },
      scrollToContent: true,
    });
  }, [excalidrawAPI]);

  //Initialize canvas when Excalidraw API is ready
  useEffect(() => {
    if(excalidrawAPI && !isInitialized) {
      console.log("Excalidraw API initialized");
      setIsInitialized(true);
    }
  }, [excalidrawAPI, isInitialized]);

  //Force re-render when diagram changes
  useEffect(() => {
    if( diagram && isInitialized) {

      console.log("New diagram detected, forcing canvas re-render...");
      console.log("Diagram Elements:", diagram.elements);
      updateCanvas(diagram)
    }
  }, [diagram, isInitialized, updateCanvas]);

  //Scroll to content when a new diagram is loaded
  useEffect(() => {
    if (excalidrawAPI && diagram) {
      setTimeout(() => {
        excalidrawAPI.scrollToContent(diagram.elements as any[], {
          fitToViewport: true,
          viewportZoomFactor: 0.8,
        });
      }, 100);
    }
  }, [excalidrawAPI, diagram]);

  //Empty State check
  if(!diagram) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-backgroun text-zinc-500">
        <div className="text-cetner p-8">
          <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-surface border border-border flex items-center justify-center">
            <svg className="w-10 h-10 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-11V5zM4 13a1 1 0 011-1h6a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
          </div>
          <p className="text-lg font-medium text-zinc-300">Diagram Canvas</p>
          <p className="text-sm mt-2 max-w-xs mx-auto">
            Your Excalidraw canvas will render here once the Agent Pipeline generates the layout.
          </p>
        </div>
      </div>
    );
  }
  return (
    //Force a key so that remount is acknowledged when a new diagram arrives
    <div className="h-full w-full">
      <Excalidraw
          initialData={{
            elements: diagram.elements as any,
            appState: diagram.appState as any,
            scrollToContent: true,
          }}
          theme='dark'
          excalidrawAPI={(api: any) => setExcalidrawAPI(api)}
          UIOptions={{
            canvasActions: {
              loadScene: false,
              saveToActiveFile: false,
              export: false, 
              saveAsImage: false,
            },
          }}
        >
          <MainMenu>
            <MainMenu.DefaultItems.ClearCanvas />
            <MainMenu.DefaultItems.Help />
          </MainMenu>
          <WelcomeScreen>
            <WelcomeScreen.Hints.MenuHint />
            <WelcomeScreen.Hints.ToolbarHint />
          </WelcomeScreen>
        </Excalidraw>
    </div>
  );
};