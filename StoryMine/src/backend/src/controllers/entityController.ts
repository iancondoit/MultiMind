import { Request, Response } from 'express';
import { cacheService } from '../services/cache';
import { 
  Entity, 
  EntityListResponse, 
  Relationship,
  NetworkNode,
  NetworkEdge,
  NetworkGraph,
  NetworkStats,
  NetworkResponse
} from '../models/storyMapModels';
import { entityService } from '../services/entityService';
import { pingStoryMapApi } from '../services/storyMapApi';

// Cache TTL values
const ENTITY_CACHE_TTL = 1800; // 30 minutes
const RELATIONSHIP_CACHE_TTL = 1800; // 30 minutes
const NETWORK_CACHE_TTL = 3600; // 1 hour
const TIMELINE_CACHE_TTL = 3600; // 1 hour

// Get environment variables for pagination
const DEFAULT_PAGE_SIZE = parseInt(process.env.DEFAULT_PAGE_SIZE || '20', 10);
const MAX_PAGE_SIZE = parseInt(process.env.MAX_PAGE_SIZE || '100', 10);

/**
 * Get entities with optional filtering
 * @param req - Express request
 * @param res - Express response
 */
export const getEntities = async (req: Request, res: Response) => {
  try {
    console.log('Entities request received');
    
    // For now, return empty results
    const response = {
      status: 'success',
      data: {
        entities: [],
        pagination: {
          limit: parseInt(req.query.limit as string) || 10,
          offset: parseInt(req.query.offset as string) || 0,
          total: 0
        }
      },
      message: 'No entities available. Awaiting StoryMap Intelligence data import.'
    };

    res.json(response);
  } catch (error) {
    console.error('Error fetching entities:', error);
    res.status(500).json({ 
      error: 'Failed to fetch entities',
      message: 'Database connection error or no data available'
    });
  }
};

/**
 * Search entities by name
 * @param req - Express request
 * @param res - Express response
 */
export const searchEntities = async (req: Request, res: Response) => {
  try {
    const query = req.query.q as string;
    console.log(`Entity search request for: ${query}`);
    
    // For now, return empty results
    res.json({
      status: 'success',
      data: {
        entities: [],
        query: query
      },
      message: 'No entities available. Awaiting StoryMap Intelligence data import.'
    });
  } catch (error) {
    console.error('Error searching entities:', error);
    res.status(500).json({ 
      error: 'Failed to search entities',
      message: 'Database connection error or no data available'
    });
  }
};

/**
 * Get a single entity by ID
 * @param req - Express request
 * @param res - Express response
 */
export const getEntity = async (req: Request, res: Response) => {
  try {
    const entityId = req.params.id;
    console.log(`Single entity request for ID: ${entityId}`);
    
    // For now, return not found
    res.status(404).json({ 
      error: 'Entity not found',
      message: 'No entities available. Awaiting StoryMap Intelligence data import.',
      entityId: entityId
    });
  } catch (error) {
    console.error('Error fetching entity:', error);
    res.status(500).json({ 
      error: 'Failed to fetch entity',
      message: 'Database connection error or no data available'
    });
  }
};

/**
 * Get entity relationships
 * @param req - Express request
 * @param res - Express response
 */
export const getEntityRelationships = async (req: Request, res: Response) => {
  try {
    const entityId = req.params.id;
    console.log(`Entity relationships request for ID: ${entityId}`);
    
    // For now, return empty relationships
    res.json({
      status: 'success',
      data: {
        entity_id: entityId,
        relationships: []
      },
      message: 'No relationship data available. Awaiting StoryMap Intelligence data import.'
    });
  } catch (error) {
    console.error('Error fetching entity relationships:', error);
    res.status(500).json({ 
      error: 'Failed to fetch entity relationships',
      message: 'Database connection error or no data available'
    });
  }
};

/**
 * Get entity network for visualization
 * @param req - Express request
 * @param res - Express response
 */
export const getEntityNetwork = async (req: Request, res: Response) => {
  try {
    const entityId = req.params.id;
    console.log(`Entity network request for ID: ${entityId}`);
    
    // For now, return empty network
    res.json({
      status: 'success',
      data: {
        nodes: [],
        edges: [],
        stats: {
          node_count: 0,
          edge_count: 0,
          density: 0
        }
      },
      message: 'No network data available. Awaiting StoryMap Intelligence data import.'
    });
  } catch (error) {
    console.error('Error fetching entity network:', error);
    res.status(500).json({ 
      error: 'Failed to fetch entity network',
      message: 'Database connection error or no data available'
    });
  }
};

/**
 * Get entity timeline
 * @param req - Express request
 * @param res - Express response
 */
export const getEntityTimeline = async (req: Request, res: Response) => {
  try {
    const entityId = req.params.id;
    console.log(`Entity timeline request for ID: ${entityId}`);
    
    // For now, return empty timeline
    res.json({
      status: 'success',
      data: {
        entity_id: entityId,
        timeline: []
      },
      message: 'No timeline data available. Awaiting StoryMap Intelligence data import.'
    });
  } catch (error) {
    console.error('Error fetching entity timeline:', error);
    res.status(500).json({ 
      error: 'Failed to fetch entity timeline',
      message: 'Database connection error or no data available'
    });
  }
}; 