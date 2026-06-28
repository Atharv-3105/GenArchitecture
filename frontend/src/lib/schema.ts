import { z } from 'zod';

// 1. Base schema for all Excalidraw elements
const BaseElementSchema = z.object({
  id: z.string(),
  type: z.string(),
  x: z.number(),
  y: z.number(),
  width: z.number(),
  height: z.number(),
  angle: z.number().default(0),
  strokeColor: z.string().default('#1e1e1e'),
  backgroundColor: z.string().default('transparent'),
  fillStyle: z.enum(['hachure', 'cross-hatch', 'solid', 'zigzag']).default('solid'),
  strokeWidth: z.number().default(2),
  strokeStyle: z.enum(['solid', 'dashed', 'dotted']).default('solid'),
  roughness: z.number().default(1),
  opacity: z.number().default(100),
  seed: z.number(),
  version: z.number().default(1),
  versionNonce: z.number(),
  isDeleted: z.boolean().default(false),
  boundElements: z.array(z.object({ id: z.string(), type: z.enum(['arrow', 'text']) })).nullable().default(null),
  updated: z.number(),
  link: z.string().nullable().default(null),
  locked: z.boolean().default(false),
  groupIds: z.array(z.string()).default([]),
  frameId: z.string().nullable().default(null),
});

// 2. Rectangle specific properties
const RectangleElementSchema = BaseElementSchema.extend({
  type: z.literal('rectangle'),
  roundness: z.object({ type: z.number() }).nullable().default({ type: 3 }),
});

// 3. Text specific properties
const TextElementSchema = BaseElementSchema.extend({
  type: z.literal('text'),
  fontSize: z.number().default(20),
  fontFamily: z.number().default(1),
  text: z.string(),
  textAlign: z.enum(['left', 'center', 'right']).default('center'),
  verticalAlign: z.enum(['top', 'middle', 'bottom']).default('middle'),
  containerId: z.string().nullable().default(null),
  originalText: z.string(),
  autoResize: z.boolean().default(true),
  lineHeight: z.number().default(1.25),
  roundness: z.null().default(null),
});

// 4. Arrow specific properties
const ArrowElementSchema = BaseElementSchema.extend({
  type: z.literal('arrow'),
  points: z.array(z.tuple([z.number(), z.number()])),
  lastCommittedPoint: z.array(z.number()).nullable().default(null),
  startBinding: z.object({
    elementId: z.string(),
    focus: z.number(),
    gap: z.number(),
  }).nullable().default(null),
  endBinding: z.object({
    elementId: z.string(),
    focus: z.number(),
    gap: z.number(),
  }).nullable().default(null),
  startArrowhead: z.enum(['arrow', 'bar', 'dot', 'triangle', 'diamond']).nullable().default(null),
  endArrowhead: z.enum(['arrow', 'bar', 'dot', 'triangle', 'diamond']).nullable().default('arrow'),
  roundness: z.object({ type: z.number() }).nullable().default({ type: 2 }),
});

// 5. Union of all valid element types
const ExcalidrawElementSchema = z.discriminatedUnion('type', [
  RectangleElementSchema,
  TextElementSchema,
  ArrowElementSchema,
]);

// 6. App State schema (simplified for our needs, allows extra properties)
const AppStateSchema = z.object({
  viewBackgroundColor: z.string().default('#ffffff'),
  theme: z.enum(['light', 'dark']).default('light'),
}).passthrough(); 

// 7. Full Diagram Payload
export const DiagramPayloadSchema = z.object({
  elements: z.array(ExcalidrawElementSchema),
  appState: AppStateSchema,
  adr_markdown: z.string().optional(), 
});

// Export inferred TypeScript types for use in our components
export type RectangleElement = z.infer<typeof RectangleElementSchema>;
export type TextElement = z.infer<typeof TextElementSchema>;
export type ArrowElement = z.infer<typeof ArrowElementSchema>;
export type ExcalidrawElement = z.infer<typeof ExcalidrawElementSchema>;
export type DiagramPayload = z.infer<typeof DiagramPayloadSchema>;

/**
 * Validates an unknown payload (simulating AI output) against the Excalidraw schema.
 * Throws a detailed error if the payload is invalid.
 */
export function validateAndParseDiagram(payload: unknown): DiagramPayload {
  try {
    return DiagramPayloadSchema.parse(payload);
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error('❌ Diagram validation failed:', error.errors);
      const formattedErrors = error.errors
        .map(e => `${e.path.join('.')}: ${e.message}`)
        .join(', ');
      throw new Error(`Invalid diagram payload: ${formattedErrors}`);
    }
    throw error;
  }
}