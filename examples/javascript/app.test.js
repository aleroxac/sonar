const { healthcheck } = require('./app');

const mockReq = {};
const mockRes = {
    json: jest.fn()
};

describe('Healthcheck', () => {
    it('should return status UP', () => {
        healthcheck(mockReq, mockRes);
        expect(mockRes.json).toHaveBeenCalledWith({ status: 'UP' });
    });
});
