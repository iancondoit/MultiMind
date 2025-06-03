import { Request, Response } from 'express';
import { cacheService } from '../services/cache';

// Cache TTL - 15 minutes for search results
const SEARCH_CACHE_TTL = 900;

/**
 * Search articles using various criteria
 * @param req - Express request
 * @param res - Express response
 */
export const searchArticles = async (req: Request, res: Response) => {
  try {
    const query = req.method === 'GET' ? req.query.q as string : req.body.query;
    console.log(`Search request for: ${query}`);
    
    if (!query) {
      return res.status(400).json({ 
        error: 'Search query is required',
        message: 'Please provide a search query parameter'
      });
    }
    
    // For now, return empty search results
    const response = {
      status: 'success',
      data: {
        query: query,
        results: [],
        pagination: {
          limit: parseInt(req.query.limit as string) || 10,
          offset: parseInt(req.query.offset as string) || 0,
          total: 0
        }
      },
      message: 'No search results available. Awaiting StoryMap Intelligence data import.'
    };

    res.json(response);
  } catch (error) {
    console.error('Error searching articles:', error);
    res.status(500).json({ 
      error: 'Failed to search articles',
      message: 'Database connection error or no data available'
    });
  }
}; 