import { z, defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';

const timelineCollection = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/timeline" }),
  schema: z.object({
    title: z.string(),
    date: z.date().or(z.string()),
    type: z.string().optional(), // 'letter' or undefined
    media: z.array(z.string()).optional().default([]),
    pdf: z.string().optional(),
    line_art: z.string().optional(),
  }),
});

export const collections = {
  'timeline': timelineCollection,
};
