// filepath: d:\DoAn\social\static\js\main.js
let loadingModal;
let currentTaskId = null;
let statusCheckInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
});

function showLoadingBrief(text = 'Processing...') {
    document.getElementById('loadingText').textContent = text;
    loadingModal.show();
}

function hideLoading() {
    loadingModal.hide();
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
}

function displayStatus(containerId, status, message, type = 'info') {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('Container not found:', containerId);
        return;
    }
    
    const alertClass = type === 'success' ? 'status-success' : 
                      type === 'error' ? 'status-error' : 
                      type === 'warning' ? 'status-warning' : 'alert-info';
    
    const icon = type === 'success' ? 'fas fa-check-circle' : 
                 type === 'error' ? 'fas fa-exclamation-circle' : 
                 type === 'warning' ? 'fas fa-exclamation-triangle' : 'fas fa-info-circle';
    
    container.innerHTML = `
        <div class="${alertClass}">
            <i class="${icon}"></i> ${message}
        </div>
    `;
}

function checkTaskStatus(taskId, containerId, onComplete = null) {
    fetch(`/task_status/${taskId}`)
        .then(response => response.json())
        .then(result => {
            if (result.status === 'running') {
                document.getElementById('loadingText').textContent = result.message || 'Processing...';
            } else if (result.status === 'success') {
                hideLoading();
                displayStatus(containerId, result.status, result.message, 'success');
                if (onComplete) onComplete(result);
                setTimeout(updateDataInfo, 1000);
            } else if (result.status === 'error') {
                hideLoading();
                displayStatus(containerId, result.status, result.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error checking task status:', error);
        });
}

async function startTopicCrawl() {
    const btn = document.getElementById('crawlTopicBtn');
    const topicInput = document.getElementById('topicInput').value.trim();
    
    console.log(`[DEBUG] startTopicCrawl called with topic: "${topicInput}"`);
    
    if (!topicInput) {
        displayStatus('topicCrawlStatus', 'error', 'Please enter a topic to search for', 'error');
        return;
    }
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Crawling...';
    
    
    try {
        const requestData = { topic: topicInput };
        console.log(`[DEBUG] Sending request to /crawl_topic with data:`, requestData);
        
        const response = await fetch('/crawl_topic', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log(`[DEBUG] Topic crawl response:`, result);
        
        if (result.status === 'started') {
            currentTaskId = result.task_id;
            displayStatus('topicCrawlStatus', 'info', 
                `Topic crawler started for: ${result.topic_input || topicInput}`, 'info');
            
            statusCheckInterval = setInterval(() => {
                checkTaskStatus(result.task_id, 'topicCrawlStatus', (finalResult) => {
                    if (finalResult.data) {
                        displayTopicResults(finalResult.data);
                    }
                });
            }, 2000);
        } else {
            hideLoading();
            displayStatus('topicCrawlStatus', result.status, result.message, result.status);
        }
        
    } catch (error) {
        hideLoading();
        console.error('Error in startTopicCrawl:', error);
        displayStatus('topicCrawlStatus', 'error', `Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-play"></i> Start Topic Crawl';
    }
}

async function startUsersCrawl() {
    const btn = document.getElementById('crawlUsersBtn');
    const userParameter = document.getElementById('userParameter').value.trim();
    
    console.log(`[DEBUG] startUsersCrawl called with parameter: "${userParameter}"`);
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Crawling...';
    
    
    try {
        const requestData = { user_parameter: userParameter };
        console.log(`[DEBUG] Sending request to /crawl_users with data:`, requestData);
        
        const response = await fetch('/crawl_users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log(`[DEBUG] Users crawl response:`, result);
        
        if (result.status === 'started') {
            currentTaskId = result.task_id;
            displayStatus('usersCrawlStatus', 'info', 
                `Users crawler started with parameter: ${result.user_parameter || 'None'}`, 'info');
            
            statusCheckInterval = setInterval(() => {
                checkTaskStatus(result.task_id, 'usersCrawlStatus', (finalResult) => {
                    if (finalResult.data) {
                        displayUsersResults(finalResult.data);
                    }
                });
            }, 2000);
        } else {
            hideLoading();
            displayStatus('usersCrawlStatus', result.status, result.message, result.status);
        }
        
    } catch (error) {
        hideLoading();
        console.error('Error in startUsersCrawl:', error);
        displayStatus('usersCrawlStatus', 'error', `Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-play"></i> Start Users Crawl';
    }
}

function displayTopicResults(data) {
    const resultsArea = document.getElementById('resultsArea');
    
    resultsArea.innerHTML = `
        <h5>🎯 Topic Crawl Results</h5>
        <div class="row mb-3">
            <div class="col-md-6">
                <strong>Topic:</strong> ${data.topic}
            </div>
            <div class="col-md-6">
                <strong>Posts Found:</strong> ${data.posts_count}
            </div>
        </div>
        <div class="alert alert-success">
            Results saved to: ${data.output_file}
        </div>
    `;
}

function displayUsersResults(data) {
    const resultsArea = document.getElementById('resultsArea');
    
    resultsArea.innerHTML = `
        <h5>👥 Users Crawl Results</h5>
        <div class="row">
            <div class="col-md-3">
                <div class="text-center">
                    <h4 class="text-primary">${data.total_users || 0}</h4>
                    <p>Total Users</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center">
                    <h4 class="text-success">${data.successful_crawls || 0}</h4>
                    <p>Successful</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center">
                    <h4 class="text-danger">${data.failed_crawls || 0}</h4>
                    <p>Failed</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center">
                    <h4 class="text-info">${data.keyword_filter || 'All'}</h4>
                    <p>Filter</p>
                </div>
            </div>
        </div>
    `;
}

async function updateDataInfo() {
    try {
        const response = await fetch('/get_data_info');
        if (response.ok) {
            location.reload();
        }
    } catch (error) {
        console.error('Error updating data info:', error);
    }
}

async function viewMainPost() {
    
    try {
        const response = await fetch('/view_main_post');
        const result = await response.json();
        hideLoading();
        
        if (result.status === 'success') {
            displayTableData('Main Post Data', result.data, [
                'username', 'text', 'timestamp', 'url', 'topic'
            ]);
        } else {
            displayStatus('resultsArea', 'error', result.message, 'error');
        }
    } catch (error) {
        hideLoading();
        displayStatus('resultsArea', 'error', `Error: ${error.message}`, 'error');
    }
}

async function viewUsersData() {
    
    try {
        const response = await fetch('/view_users_data');
        const result = await response.json();
        hideLoading();
        
        if (result.status === 'success') {
            if (result.data_type === 'threads') {
                // Display all threads/comments
                displayTableData('Users Data - All Threads/Comments', result.data, [
                    'username', 'full_name', 'followers', 'is_verified', 
                    'thread_text', 'published_on', 'like_count', 'reply_count', 'thread_url'
                ]);
            } else {
                // Fallback to original format
                const usersTable = result.data.map(userItem => {
                    const user = userItem.user || {};
                    const threads = userItem.threads || [];
                    
                    return {
                        username: user.username || 'N/A',
                        full_name: user.full_name || 'N/A',
                        followers: user.followers || 0,
                        posts_count: threads.length,
                        verified: user.is_verified ? 'Yes' : 'No'
                    };
                });
                
                displayTableData('Users Data', usersTable, [
                    'username', 'full_name', 'followers', 'posts_count', 'verified'
                ]);
            }
        } else {
            displayStatus('resultsArea', 'error', result.message, 'error');
        }
    } catch (error) {
        hideLoading();
        displayStatus('resultsArea', 'error', `Error: ${error.message}`, 'error');
    }
}

function displayTableData(title, data, columns) {
    const resultsArea = document.getElementById('resultsArea');
    
    if (!data || data.length === 0) {
        resultsArea.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i> No data available for ${title}
            </div>
        `;
        return;
    }
    
    let tableHtml = `
        <h5>${title}</h5>
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        ${columns.map(col => `<th>${col.replace('_', ' ').toUpperCase()}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.forEach(row => {
        tableHtml += '<tr>';
        columns.forEach(col => {
            let value = row[col] || '';
            
            // Special handling for URLs
            if (col === 'thread_url' && value) {
                value = `<a href="${value}" target="_blank" class="btn btn-sm btn-outline-primary">View</a>`;
            }
            // Special handling for long text
            else if (col === 'thread_text' && typeof value === 'string' && value.length > 100) {
                value = `<span title="${value}">${value.substring(0, 100)}...</span>`;
            }
            // Other text truncation
            else if (typeof value === 'string' && value.length > 50 && col !== 'thread_url') {
                value = value.substring(0, 50) + '...';
            }
            
            tableHtml += `<td>${value}</td>`;
        });
        tableHtml += '</tr>';
    });
    
    tableHtml += `
                </tbody>
            </table>
        </div>
    `;
    
    resultsArea.innerHTML = tableHtml;
}