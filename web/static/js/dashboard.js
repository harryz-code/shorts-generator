/**
 * Dashboard JavaScript
 * Handles all dashboard interactions and API calls
 */

class Dashboard {
    constructor() {
        this.refreshInterval = null;
        this.currentFilters = {
            theme: '',
            status: ''
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.startAutoRefresh();
    }
    
    setupEventListeners() {
        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadDashboardData();
        });
        
        // Generate content button
        document.getElementById('generate-btn').addEventListener('click', () => {
            this.showGenerateModal();
        });
        
        // Upload queue button
        document.getElementById('upload-btn').addEventListener('click', () => {
            this.uploadQueue();
        });
        
        // Schedule content button
        document.getElementById('schedule-btn').addEventListener('click', () => {
            this.showScheduleModal();
        });
        
        // Settings button
        document.getElementById('settings-btn').addEventListener('click', () => {
            this.showSettingsModal();
        });
        
        // Filter changes
        document.getElementById('filter-theme').addEventListener('change', (e) => {
            this.currentFilters.theme = e.target.value;
            this.filterContent();
        });
        
        document.getElementById('filter-status').addEventListener('change', (e) => {
            this.currentFilters.status = e.target.value;
            this.filterContent();
        });
        
        // Modal events
        document.getElementById('cancel-generate').addEventListener('click', () => {
            this.hideGenerateModal();
        });
        
        document.getElementById('confirm-generate').addEventListener('click', () => {
            this.generateContent();
        });
    }
    
    async loadDashboardData() {
        try {
            this.showLoading(true);
            
            // Load system status
            const statusResponse = await fetch('/api/status');
            const status = await statusResponse.json();
            this.updateStatusCards(status);
            
            // Load content
            const contentResponse = await fetch('/api/content');
            const content = await contentResponse.json();
            this.updateContentTable(content);
            
            // Load stats
            const statsResponse = await fetch('/api/stats');
            const stats = await statsResponse.json();
            this.updateStats(stats);
            
            this.updateLastUpdateTime();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
        } finally {
            this.showLoading(false);
        }
    }
    
    updateStatusCards(status) {
        // Update status indicators
        if (status.content_agent) {
            this.updateStatusIndicator('content-model-status', status.content_agent.status);
        }
        if (status.video_agent) {
            this.updateStatusIndicator('video-model-status', status.video_agent.status);
        }
        if (status.audio_agent) {
            this.updateStatusIndicator('audio-model-status', status.audio_agent.status);
        }
        
        // Update platform status
        if (status.platforms) {
            this.updatePlatformStatus('youtube-status', status.platforms.youtube);
            this.updatePlatformStatus('instagram-status', status.platforms.instagram);
            this.updatePlatformStatus('tiktok-status', status.platforms.tiktok);
        }
    }
    
    updateStatusIndicator(elementId, status) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const isReady = status === 'ready' || status === 'connected';
        element.className = `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            isReady ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`;
        element.innerHTML = `<i class="fas fa-${isReady ? 'check' : 'times'} mr-1"></i>${
            isReady ? 'Ready' : 'Error'
        }`;
    }
    
    updatePlatformStatus(elementId, status) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        let className, icon, text;
        
        switch (status) {
            case 'connected':
                className = 'bg-green-100 text-green-800';
                icon = 'check';
                text = 'Connected';
                break;
            case 'pending':
                className = 'bg-yellow-100 text-yellow-800';
                icon = 'exclamation-triangle';
                text = 'Pending';
                break;
            case 'error':
                className = 'bg-red-100 text-red-800';
                icon = 'times';
                text = 'Error';
                break;
            default:
                className = 'bg-gray-100 text-gray-800';
                icon = 'question';
                text = 'Unknown';
        }
        
        element.className = `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`;
        element.innerHTML = `<i class="fas fa-${icon} mr-1"></i>${text}`;
    }
    
    updateContentTable(content) {
        const tbody = document.getElementById('content-table-body');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (!content || content.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="px-6 py-4 text-center text-gray-500">
                        No content found
                    </td>
                </tr>
            `;
            return;
        }
        
        content.forEach(item => {
            const row = this.createContentRow(item);
            tbody.appendChild(row);
        });
    }
    
    createContentRow(item) {
        const row = document.createElement('tr');
        row.className = 'fade-in';
        
        const statusBadge = this.getStatusBadge(item.status);
        const actions = this.getActionButtons(item);
        
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">${item.title}</div>
                <div class="text-sm text-gray-500">${item.description?.substring(0, 50)}...</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    ${item.theme || 'Unknown'}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${statusBadge}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${this.formatDate(item.created_at)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                ${actions}
            </td>
        `;
        
        return row;
    }
    
    getStatusBadge(status) {
        const statusMap = {
            'generated': { class: 'success', text: 'Generated' },
            'uploaded': { class: 'success', text: 'Uploaded' },
            'failed': { class: 'error', text: 'Failed' },
            'queued': { class: 'warning', text: 'Queued' },
            'processing': { class: 'info', text: 'Processing' }
        };
        
        const statusInfo = statusMap[status] || { class: 'info', text: status || 'Unknown' };
        
        return `<span class="status-badge ${statusInfo.class}">${statusInfo.text}</span>`;
    }
    
    getActionButtons(item) {
        let buttons = '';
        
        if (item.status === 'generated') {
            buttons += `<button onclick="dashboard.uploadContent('${item.id}')" class="text-green-600 hover:text-green-900 mr-2">Upload</button>`;
        }
        
        if (item.status === 'failed') {
            buttons += `<button onclick="dashboard.retryContent('${item.id}')" class="text-blue-600 hover:text-blue-900 mr-2">Retry</button>`;
        }
        
        buttons += `<button onclick="dashboard.viewContent('${item.id}')" class="text-gray-600 hover:text-gray-900">View</button>`;
        
        return buttons;
    }
    
    updateStats(stats) {
        // Update dashboard cards
        if (stats.total_videos !== undefined) {
            document.getElementById('total-videos').textContent = stats.total_videos;
        }
        if (stats.uploaded_today !== undefined) {
            document.getElementById('uploaded-today').textContent = stats.uploaded_today;
        }
        if (stats.in_queue !== undefined) {
            document.getElementById('in-queue').textContent = stats.in_queue;
        }
        if (stats.success_rate !== undefined) {
            document.getElementById('success-rate').textContent = `${stats.success_rate}%`;
        }
    }
    
    filterContent() {
        const rows = document.querySelectorAll('#content-table-body tr');
        
        rows.forEach(row => {
            const theme = row.querySelector('td:nth-child(2) span')?.textContent?.toLowerCase();
            const status = row.querySelector('td:nth-child(3) span')?.textContent?.toLowerCase();
            
            const themeMatch = !this.currentFilters.theme || theme === this.currentFilters.theme.toLowerCase();
            const statusMatch = !this.currentFilters.status || status === this.currentFilters.status.toLowerCase();
            
            row.style.display = themeMatch && statusMatch ? '' : 'none';
        });
    }
    
    showGenerateModal() {
        document.getElementById('generate-modal').classList.remove('hidden');
    }
    
    hideGenerateModal() {
        document.getElementById('generate-modal').classList.add('hidden');
    }
    
    async generateContent() {
        const count = parseInt(document.getElementById('generate-count').value);
        const theme = document.getElementById('generate-theme').value;
        
        try {
            this.hideGenerateModal();
            this.showLoading(true);
            
            const response = await fetch('/api/generate-content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ count, theme })
            });
            
            if (response.ok) {
                this.showSuccess(`Started generating ${count} videos with theme: ${theme}`);
                // Reload data after a delay to show progress
                setTimeout(() => this.loadDashboardData(), 2000);
            } else {
                throw new Error('Failed to start generation');
            }
            
        } catch (error) {
            console.error('Error generating content:', error);
            this.showError('Failed to generate content');
        } finally {
            this.showLoading(false);
        }
    }
    
    async uploadQueue() {
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/upload-queue', {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showSuccess('Upload queue started');
                setTimeout(() => this.loadDashboardData(), 2000);
            } else {
                throw new Error('Failed to start upload queue');
            }
            
        } catch (error) {
            console.error('Error starting upload queue:', error);
            this.showError('Failed to start upload queue');
        } finally {
            this.showLoading(false);
        }
    }
    
    async uploadContent(contentId) {
        try {
            this.showLoading(true);
            
            const response = await fetch(`/api/upload/${contentId}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showSuccess('Content upload started');
                setTimeout(() => this.loadDashboardData(), 2000);
            } else {
                throw new Error('Failed to upload content');
            }
            
        } catch (error) {
            console.error('Error uploading content:', error);
            this.showError('Failed to upload content');
        } finally {
            this.showLoading(false);
        }
    }
    
    async retryContent(contentId) {
        try {
            this.showLoading(true);
            
            const response = await fetch(`/api/retry/${contentId}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showSuccess('Content retry started');
                setTimeout(() => this.loadDashboardData(), 2000);
            } else {
                throw new Error('Failed to retry content');
            }
            
        } catch (error) {
            console.error('Error retrying content:', error);
            this.showError('Failed to retry content');
        } finally {
            this.showLoading(false);
        }
    }
    
    viewContent(contentId) {
        // TODO: Implement content viewer modal
        console.log('View content:', contentId);
    }
    
    showScheduleModal() {
        // TODO: Implement schedule modal
        this.showInfo('Schedule functionality coming soon!');
    }
    
    showSettingsModal() {
        // TODO: Implement settings modal
        this.showInfo('Settings functionality coming soon!');
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.toggle('hidden', !show);
        }
    }
    
    showSuccess(message) {
        this.showMessage(message, 'success');
    }
    
    showError(message) {
        this.showMessage(message, 'error');
    }
    
    showInfo(message) {
        this.showMessage(message, 'info');
    }
    
    showMessage(message, type = 'info') {
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = `fixed top-4 right-4 z-50 message p-4 rounded-md shadow-lg ${
            type === 'success' ? 'bg-green-500 text-white' :
            type === 'error' ? 'bg-red-500 text-white' :
            'bg-blue-500 text-white'
        }`;
        messageEl.textContent = message;
        
        document.body.appendChild(messageEl);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.parentNode.removeChild(messageEl);
            }
        }, 3000);
    }
    
    updateLastUpdateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        document.getElementById('last-update').textContent = `Last updated: ${timeString}`;
    }
    
    startAutoRefresh() {
        // Refresh every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 30000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.stopAutoRefresh();
    }
});
