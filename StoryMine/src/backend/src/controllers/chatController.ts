import { Request, Response } from 'express';
import { cacheService } from '../services/cache';
import { claudeService } from '../services/claudeService';
import { entityService } from '../services/entityService';
import { ArticleSource, ExtendedEntity } from '../models/extendedTypes';
import { Article, SearchResultItem } from '../models/storyMapModels';

// Cache TTL values
const SEARCH_CACHE_TTL = 900; // 15 minutes
const ENTITY_CACHE_TTL = 1800; // 30 minutes

// Entity query patterns
const ENTITY_QUERY_PATTERNS = [
  /who is ([^?]+)/i,
  /tell me about ([^?]+)/i,
  /what do you know about ([^?]+)/i,
  /information on ([^?]+)/i,
  /details about ([^?]+)/i,
  /who was ([^?]+)/i,
  /what is ([^?]+)/i
];

// Timeline query patterns
const TIMELINE_QUERY_PATTERNS = [
  /timeline for ([^?]+)/i,
  /history of ([^?]+)/i,
  /chronology of ([^?]+)/i,
  /when did ([^?]+)/i,
  /events related to ([^?]+)/i
];

// Relationship query patterns
const RELATIONSHIP_QUERY_PATTERNS = [
  /relationship between ([^?]+) and ([^?]+)/i,
  /how is ([^?]+) connected to ([^?]+)/i,
  /connection between ([^?]+) and ([^?]+)/i,
  /how are ([^?]+) and ([^?]+) related/i,
  /associations of ([^?]+)/i,
  /who is ([^?]+) connected to/i
];

// Random content query patterns
const RANDOM_QUERY_PATTERNS = [
  /random (person|individual|figure|name)/i,
  /random (story|article|news|event)/i,
  /interesting (story|article|news|event)/i
];

/**
 * Check if a query is asking about an entity
 */
function isEntityQuery(query: string): boolean {
  return ENTITY_QUERY_PATTERNS.some(pattern => pattern.test(query));
}

/**
 * Check if a query is asking for a timeline
 */
function isTimelineQuery(query: string): boolean {
  return TIMELINE_QUERY_PATTERNS.some(pattern => pattern.test(query));
}

/**
 * Check if a query is asking about relationships
 */
function isRelationshipQuery(query: string): boolean {
  return RELATIONSHIP_QUERY_PATTERNS.some(pattern => pattern.test(query));
}

/**
 * Check if a query is asking for random content
 */
function isRandomContentQuery(query: string): boolean {
  return RANDOM_QUERY_PATTERNS.some(pattern => pattern.test(query));
}

/**
 * Extract potential entity name from a query
 * @param query - The query to extract entity name from
 * @returns Potential entity name or null
 */
function extractPotentialEntityName(query: string): string | null {
  // Try each pattern
  for (const pattern of [...ENTITY_QUERY_PATTERNS, ...TIMELINE_QUERY_PATTERNS]) {
    const match = query.match(pattern);
    if (match && match[1]) {
      return match[1].trim();
    }
  }
  
  // Handle relationship patterns differently
  for (const pattern of RELATIONSHIP_QUERY_PATTERNS) {
    const match = query.match(pattern);
    if (match) {
      // If we have two entities, return the first one
      if (match[2]) {
        return match[1].trim();
      } else if (match[1]) {
        return match[1].trim();
      }
    }
  }
  
  return null;
}

/**
 * Generate a timeline for an entity
 * @param entityId - The entity ID to generate timeline for
 * @returns Array of timeline entries
 */
async function generateEntityTimeline(entityId: string): Promise<any[]> {
  try {
    // Get entity timeline from the entity service
    const timeline = await entityService.getEntityTimeline(entityId);
    
    if (timeline && timeline.length > 0) {
      return timeline.map(entry => ({
        date: entry.date,
        title: entry.title,
        content: entry.content,
        source: entry.source || 'Unknown',
        articleId: entry.article_id
      }));
    }
    
    return [];
  } catch (error) {
    console.error(`Error generating timeline for entity ${entityId}:`, error);
    return [];
  }
}

/**
 * Handle chat message
 * @param req - Express request
 * @param res - Express response
 */
export const handleChatMessage = async (req: Request, res: Response) => {
  try {
    const { message, conversationId = 'default' } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    console.log('Processing user message:', message);
    
    // Context to be sent to the Claude service
    const context: any = {
      query: message,
      articles: [],
      entities: [],
      isEntityQuery: false,
      note: 'StoryMine is currently ready to receive StoryMap Intelligence data. Responses are based on Claude\'s general historical knowledge until data is imported.'
    };
    
    console.log(`Sending query to Claude with general knowledge context`);
    
    // Get a response from Jordi using Claude's built-in knowledge
    const jordiResponse = await claudeService.getJordiResponse(message, context, conversationId);
    
    // Prepare sources from context (empty for now)
    const sources: ArticleSource[] = [];
    
    // Return the response with metadata
    return res.json({
      message: jordiResponse.text,
      sources,
      entities: context.entities || [],
      timeline: [],
      usage: jordiResponse.usage,
      note: 'Responses currently based on Claude\'s general historical knowledge. Database integration coming soon.'
    });
  } catch (error) {
    console.error('Error handling chat message:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}; 