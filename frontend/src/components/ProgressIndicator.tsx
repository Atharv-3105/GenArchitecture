import React from 'react';
import { Check, Loader2, AlertCircle } from 'lucide-react';

interface ProgressIndicatorProps {
    status: 'idle' | 'streaming' | 'complete' | 'error';
    currentNode: string | null;
    completedNodes: string[];
    error: string | null;
}

const STEPS = [
    {
        id: 'parser', label: 'Parsing Intent'
    },
    {
        id: 'architecutre', label: 'Designing Architecture'
    },
    {
        id: 'layout', label: 'Calculating Layout'
    },
    {
        id: 'style', label: 'Applying Styles'
    },
    {
        id: 'validator', label: 'Validating Diagram'
    },
];

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({status, currentNode, completedNodes, error}) => {
    if (status == 'idle') return null;

    return (
        <div className="bg-surface border border-border rounded-lg p-4 mb-4">
            <h3 className="text-sm font-semibold text-zinc-300 mb-3">Generation Progress</h3>
            <ul className="space-y-2">
                {STEPS.map((step) => {
                    const isCompleted = completedNodes.includes(step.id);
                    const isCurrent = currentNode === step.id;

                    return (
                        <li key = {step.id} className='flex items-center gap-3 text-sm'>
                            {isCompleted ? (
                                <div className="w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center">
                                    <Check className="w-3 h-3 text-green-400" />
                                </div>
                            ): isCurrent ? (
                                <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center">
                                    <Loader2 className="w-3 h-3 text-primary animate-spin"/>
                                </div>
                            ) : (
                                <div className="w-5 h-5 rounded-full bg-zinc-800 flex items-center justify-center">
                                    <div className="w-2 h-2 rounded-full bg-zinc-600" />
                                </div>
                            )}
                            <span className= {isCompleted ? 'text-zinc-400' : isCurrent ? 'text-white font-medium' : 'text-zinc-500'}>
                                {step.label}
                            </span>
                        </li>
                    );
                })}
            </ul>

            {status === 'error' && error && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-md flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-400"> {error}</p>
                </div>
            )}
        </div>
    );
};