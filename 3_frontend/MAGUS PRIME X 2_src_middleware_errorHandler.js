```javascript
  function errorHandler(err, req, res, next) {
    console.error('Error:', err);
    res.status(500).json({
      success: false,
      message: 'An error occurred while processing your request.',
      details: process.env.NODE_ENV === 'development' ? err.message : undefined,
    });
  }

  module.exports = errorHandler;
  ```;
