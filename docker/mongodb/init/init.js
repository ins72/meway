// MongoDB initialization script for Mewayz
db = db.getSiblingDB('mewayz');

// Create collections
db.createCollection('users');
db.createCollection('workspaces');
db.createCollection('subscriptions');
db.createCollection('payments');
db.createCollection('integrations');
db.createCollection('ai_usage');
db.createCollection('social_posts');
db.createCollection('analytics');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.workspaces.createIndex({ "owner_id": 1 });
db.workspaces.createIndex({ "members.user_id": 1 });
db.subscriptions.createIndex({ "user_id": 1 });
db.subscriptions.createIndex({ "workspace_id": 1 });
db.payments.createIndex({ "user_id": 1 });
db.payments.createIndex({ "subscription_id": 1 });
db.ai_usage.createIndex({ "user_id": 1 });
db.ai_usage.createIndex({ "workspace_id": 1 });
db.social_posts.createIndex({ "user_id": 1 });
db.social_posts.createIndex({ "workspace_id": 1 });
db.analytics.createIndex({ "user_id": 1 });
db.analytics.createIndex({ "workspace_id": 1 });

print('Mewayz database initialized successfully!'); 