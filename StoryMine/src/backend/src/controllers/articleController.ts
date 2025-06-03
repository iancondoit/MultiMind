import { Request, Response } from 'express';
import { cacheService } from '../services/cache';
import { Article } from '../models/storyMapModels';

// Cache TTL - 1 hour for articles
const CACHE_TTL = 3600;

/**
 * Get all articles with pagination
 * @param req - Express request
 * @param res - Express response
 */
export const getArticles = async (req: Request, res: Response) => {
  try {
    console.log('Article request received');
    
    // For now, return empty results indicating no data available
    const response = {
      status: 'success',
      data: {
        articles: [],
        pagination: {
          limit: parseInt(req.query.limit as string) || 10,
          offset: parseInt(req.query.offset as string) || 0,
          total: 0
        }
      },
      message: 'No articles available. Awaiting StoryMap Intelligence data import.'
    };

    res.json(response);
  } catch (error) {
    console.error('Error fetching articles:', error);
    res.status(500).json({ 
      error: 'Failed to fetch articles',
      message: 'Database connection error or no data available'
    });
  }
};

/**
 * Get a single article by ID
 * @param req - Express request
 * @param res - Express response
 */
export const getArticle = async (req: Request, res: Response) => {
  try {
    const articleId = req.params.id;
    console.log(`Single article request for ID: ${articleId}`);
    
    // For now, return not found
    res.status(404).json({ 
      error: 'Article not found',
      message: 'No articles available. Awaiting StoryMap Intelligence data import.',
      articleId: articleId
    });
  } catch (error) {
    console.error('Error fetching article:', error);
    res.status(500).json({ 
      error: 'Failed to fetch article',
      message: 'Database connection error or no data available'
    });
  }
}; 