import { z, defineCollection } from 'astro:content';

const timelineCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.string(),
    type: z.string().optional(), // 'letter' or undefined
    media: z.array(z.string()).optional().default([]),
  }),
});

export const collections = {
  'timeline': timelineCollection,
};
