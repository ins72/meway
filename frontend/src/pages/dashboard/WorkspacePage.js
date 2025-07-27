import React
import ApiService from '../../services/apiService';, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BuildingOfficeIcon, 
  PlusIcon, 
  CogIcon,
  UserGroupIcon,
  ShareIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ClockIcon,
  BellIcon,
  StarIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';
import Button from '../../components/Button';

const WorkspacePage = () => {
  const [workspaces, setWorkspaces] = useState([]);
  const [currentWorkspace, setCurrentWorkspace] = useState(null);
  const [teamMembers, setTeamMembers] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadWorkspaceData();
  }, []);

  const loadWorkspaceData = async () => {
    try {
      // Real API data
      const workspaces = await ApiService.getWorkspaces();
      setWorkspaces(workspaces);
        {
          id: 1,
          name: 'Marketing Agency Pro',
          description: 'Main workspace for our digital marketing agency',
          type: 'Agency',
          members: 8,
          projects: 12,
          created: '2025-01-15',
          status: 'active',
          plan: 'Enterprise',
          isOwner: true
        },
        {
          id: 2,
          name: 'E-commerce Store',
          description: 'Online store management and growth',
          type: 'E-commerce',
          members: 3,
          projects: 5,
          created: '2025-02-10',
          status: 'active',
          plan: 'Professional',
          isOwner: true
        },
        {
          id: 3,
          name: 'Content Creator Hub',
          description: 'Personal brand and content creation',
          type: 'Creator',
          members: 1,
          projects: 8,
          created: '2025-03-05',
          status: 'active',
          plan: 'Creator Pro',
          isOwner: false
        }
      ]);

      setCurrentWorkspace(workspaces[0] || null);

      const members = await ApiService.getWorkspace(workspaceId).members;
      setTeamMembers(members);
        {
          id: 1,
          name: 'Sarah Johnson',
          email: 'sarah@agency.com',
          role: 'Admin',
          avatar: null,
          status: 'online',
          joinDate: '2025-01-15',
          lastActive: 'Active now'
        },
        {
          id: 2,
          name: 'Mike Chen',
          email: 'mike@agency.com',
          role: 'Editor',
          avatar: null,
          status: 'offline',
          joinDate: '2025-01-20',
          lastActive: '2 hours ago'
        },
        {
          id: 3,
          name: 'Emily Davis',
          email: 'emily@agency.com',
          role: 'Viewer',
          avatar: null,
          status: 'away',
          joinDate: '2025-02-01',
          lastActive: '15 minutes ago'
        }
      ]);

      setRecentActivity([
        {
          id: 1,
          user: 'Sarah Johnson',
          action: 'created a new campaign',
          target: 'Summer Sale 2025',
          time: '2 minutes ago',
          type: 'create'
        },
        {
          id: 2,
          user: 'Mike Chen',
          action: 'updated bio site',
          target: 'Company Profile',
          time: '15 minutes ago',
          type: 'update'
        },
        {
          id: 3,
          user: 'Emily Davis',
          action: 'shared a template',
          target: 'Newsletter Template v2',
          time: '1 hour ago',
          type: 'share'
        },
        {
          id: 4,
          user: 'Sarah Johnson',
          action: 'invited team member',
          target: 'john@agency.com',
          time: '3 hours ago',
          type: 'invite'
        }
      ]);

      setAnalytics({
        totalProjects: 25,
        activeMembers: 8,
        completedTasks: 156,
        storageUsed: 68,
        storageLimit: 100
      });
    } catch (error) {
      console.error('Failed to load workspace data:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, change, icon: Icon, color = 'primary' }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-elevated p-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-secondary">{title}</p>
          <p className="text-3xl font-bold text-primary mt-2">{value}</p>
          {change && (
            <p className={`text-sm mt-2 ${change > 0 ? 'text-accent-success' : 'text-accent-danger'}`}>
              {change > 0 ? '+' : ''}{change}% vs last month
            </p>
          )}
        </div>
        <div className={`bg-gradient-${color} p-3 rounded-lg`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
      </div>
    </motion.div>
  );

  const WorkspaceCard = ({ workspace }) => (
    <div className="card-elevated p-6 hover-surface transition-colors cursor-pointer">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-primary rounded-lg flex items-center justify-center">
            <BuildingOfficeIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-primary">{workspace.name}</h3>
            <p className="text-sm text-secondary">{workspace.type}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {workspace.isOwner && (
            <StarIcon className="w-4 h-4 text-yellow-500" />
          )}
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            workspace.status === 'active'
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
          }`}>
            {workspace.status}
          </span>
        </div>
      </div>

      <p className="text-secondary text-sm mb-4">{workspace.description}</p>

      <div className="grid grid-cols-2 gap-4 text-sm mb-4">
        <div>
          <p className="text-secondary">Members</p>
          <p className="font-medium text-primary">{workspace.members}</p>
        </div>
        <div>
          <p className="text-secondary">Projects</p>
          <p className="font-medium text-primary">{workspace.projects}</p>
        </div>
        <div>
          <p className="text-secondary">Plan</p>
          <p className="font-medium text-primary">{workspace.plan}</p>
        </div>
        <div>
          <p className="text-secondary">Created</p>
          <p className="font-medium text-primary">{workspace.created}</p>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-default">
        <Button variant="secondary" size="small">
          <EyeIcon className="w-4 h-4 mr-1" />
          View
        </Button>
        <div className="flex items-center space-x-2">
          <button className="p-2 text-secondary hover:text-primary">
            <CogIcon className="w-4 h-4" />
          </button>
          <button className="p-2 text-secondary hover:text-primary">
            <ShareIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  const TeamMemberCard = ({ member }) => (
    <div className="card p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-10 h-10 bg-gradient-primary rounded-full flex items-center justify-center">
              <span className="text-white font-bold">{member.name.charAt(0)}</span>
            </div>
            <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white dark:border-gray-800 ${
              member.status === 'online' ? 'bg-green-500' :
              member.status === 'away' ? 'bg-yellow-500' : 'bg-gray-400'
            }`}></div>
          </div>
          <div>
            <h4 className="font-medium text-primary">{member.name}</h4>
            <p className="text-sm text-secondary">{member.email}</p>
            <p className="text-xs text-secondary">{member.lastActive}</p>
          </div>
        </div>
        <div className="text-right">
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            member.role === 'Admin' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
            member.role === 'Editor' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
            'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
          }`}>
            {member.role}
          </span>
          <p className="text-xs text-secondary mt-1">Joined {member.joinDate}</p>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner w-8 h-8 text-accent-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-primary">Workspaces</h1>
          <p className="text-secondary mt-1">Manage your teams and collaborative projects</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="secondary">
            <UserGroupIcon className="w-4 h-4 mr-2" />
            Invite Team
          </Button>
          <Button>
            <PlusIcon className="w-4 h-4 mr-2" />
            Create Workspace
          </Button>
        </div>
      </div>

      {/* Current Workspace Banner */}
      {currentWorkspace && (
        <div className="bg-gradient-primary rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">{currentWorkspace.name}</h2>
              <p className="text-blue-100 mb-4">{currentWorkspace.description}</p>
              <div className="flex items-center space-x-6 text-sm">
                <div className="flex items-center space-x-2">
                  <UserGroupIcon className="w-4 h-4" />
                  <span>{currentWorkspace.members} members</span>
                </div>
                <div className="flex items-center space-x-2">
                  <DocumentTextIcon className="w-4 h-4" />
                  <span>{currentWorkspace.projects} projects</span>
                </div>
                <div className="flex items-center space-x-2">
                  <StarIcon className="w-4 h-4" />
                  <span>{currentWorkspace.plan}</span>
                </div>
              </div>
            </div>
            <Button variant="secondary">
              <CogIcon className="w-4 h-4 mr-2" />
              Manage
            </Button>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-default">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview' },
            { id: 'workspaces', name: 'All Workspaces' },
            { id: 'team', name: 'Team Members' },
            { id: 'activity', name: 'Activity' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-accent-primary text-accent-primary'
                  : 'border-transparent text-secondary hover:text-primary hover:border-gray-300'
              }`}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Content based on active tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Analytics Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Total Projects"
              value={analytics.totalProjects.toString()}
              change={15.2}
              icon={DocumentTextIcon}
              color="primary"
            />
            <StatCard
              title="Active Members"
              value={analytics.activeMembers.toString()}
              change={8.1}
              icon={UserGroupIcon}
              color="success"
            />
            <StatCard
              title="Completed Tasks"
              value={analytics.completedTasks.toString()}
              change={23.5}
              icon={ChartBarIcon}
              color="warning"
            />
            <StatCard
              title="Storage Used"
              value={`${analytics.storageUsed}%`}
              icon={BuildingOfficeIcon}
              color="primary"
            />
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <button className="card-elevated p-6 text-left hover-surface transition-colors">
              <PlusIcon className="w-8 h-8 text-accent-primary mb-4" />
              <h3 className="font-semibold text-primary mb-2">Create Project</h3>
              <p className="text-secondary">Start a new collaborative project</p>
            </button>
            <button className="card-elevated p-6 text-left hover-surface transition-colors">
              <UserGroupIcon className="w-8 h-8 text-accent-primary mb-4" />
              <h3 className="font-semibold text-primary mb-2">Invite Members</h3>
              <p className="text-secondary">Add team members to your workspace</p>
            </button>
            <button className="card-elevated p-6 text-left hover-surface transition-colors">
              <CogIcon className="w-8 h-8 text-accent-primary mb-4" />
              <h3 className="font-semibold text-primary mb-2">Workspace Settings</h3>
              <p className="text-secondary">Configure permissions and preferences</p>
            </button>
          </div>

          {/* Recent Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h2 className="text-xl font-semibold text-primary mb-4">Recent Activity</h2>
              <div className="space-y-4">
                {recentActivity.slice(0, 4).map((activity) => (
                  <div key={activity.id} className="card p-4">
                    <div className="flex items-start space-x-3">
                      <div className={`w-2 h-2 rounded-full mt-2 ${
                        activity.type === 'create' ? 'bg-green-500' :
                        activity.type === 'update' ? 'bg-blue-500' :
                        activity.type === 'share' ? 'bg-purple-500' : 'bg-orange-500'
                      }`}></div>
                      <div className="flex-1">
                        <p className="text-primary">
                          <span className="font-medium">{activity.user}</span> {activity.action}{' '}
                          <span className="font-medium">{activity.target}</span>
                        </p>
                        <p className="text-secondary text-sm">{activity.time}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h2 className="text-xl font-semibold text-primary mb-4">Active Team Members</h2>
              <div className="space-y-4">
                {teamMembers.filter(m => m.status !== 'offline').map((member) => (
                  <div key={member.id} className="card p-4">
                    <div className="flex items-center space-x-3">
                      <div className="relative">
                        <div className="w-8 h-8 bg-gradient-primary rounded-full flex items-center justify-center">
                          <span className="text-white text-sm font-bold">{member.name.charAt(0)}</span>
                        </div>
                        <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white dark:border-gray-800 ${
                          member.status === 'online' ? 'bg-green-500' : 'bg-yellow-500'
                        }`}></div>
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-primary">{member.name}</p>
                        <p className="text-sm text-secondary">{member.role} • {member.lastActive}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'workspaces' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-primary">All Workspaces</h2>
            <div className="flex items-center space-x-3">
              <select className="input px-3 py-2 rounded-md">
                <option>All Types</option>
                <option>Agency</option>
                <option>E-commerce</option>
                <option>Creator</option>
              </select>
              <select className="input px-3 py-2 rounded-md">
                <option>All Status</option>
                <option>Active</option>
                <option>Paused</option>
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {workspaces.map((workspace) => (
              <WorkspaceCard key={workspace.id} workspace={workspace} />
            ))}
          </div>
        </div>
      )}

      {activeTab === 'team' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-primary">Team Members</h2>
            <div className="flex items-center space-x-3">
              <Button variant="secondary">
                <ShareIcon className="w-4 h-4 mr-2" />
                Invite Link
              </Button>
              <Button>
                <PlusIcon className="w-4 h-4 mr-2" />
                Invite Member
              </Button>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {teamMembers.map((member) => (
              <TeamMemberCard key={member.id} member={member} />
            ))}
          </div>
        </div>
      )}

      {activeTab === 'activity' && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-primary">Workspace Activity</h2>
          
          <div className="card-elevated">
            <div className="p-6">
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-4 p-4 hover-surface rounded-lg transition-colors">
                    <div className={`w-3 h-3 rounded-full mt-2 ${
                      activity.type === 'create' ? 'bg-green-500' :
                      activity.type === 'update' ? 'bg-blue-500' :
                      activity.type === 'share' ? 'bg-purple-500' : 'bg-orange-500'
                    }`}></div>
                    <div className="flex-1">
                      <p className="text-primary">
                        <span className="font-medium">{activity.user}</span> {activity.action}{' '}
                        <span className="font-medium text-accent-primary">{activity.target}</span>
                      </p>
                      <p className="text-secondary text-sm mt-1">{activity.time}</p>
                    </div>
                    <Button variant="secondary" size="small">
                      <ArrowRightIcon className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkspacePage;