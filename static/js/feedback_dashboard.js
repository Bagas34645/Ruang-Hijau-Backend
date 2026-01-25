/**
 * Feedback Dashboard JavaScript
 * Handles sentiment analysis visualization and feedback management
 */

// Chart instances
let sentimentChart = null;
let ratingChart = null;
let sentimentTrendChart = null;
let categorySentimentChart = null;

// API Base
const FEEDBACK_API_BASE = '/api/feedback';

// Initialize feedback section when loaded
function initFeedbackDashboard() {
    loadFeedbackData();

    // Add event listener for time range selector
    const timeRangeSelect = document.getElementById('feedbackTimeRange');
    if (timeRangeSelect) {
        timeRangeSelect.addEventListener('change', () => {
            loadFeedbackData();
        });
    }
}

// Refresh all feedback data
function refreshFeedbackData() {
    loadFeedbackData();
}

// Load all feedback data
async function loadFeedbackData() {
    try {
        const days = document.getElementById('feedbackTimeRange')?.value || 30;

        // Load all data in parallel
        const [statsRes, sentimentRes, trendRes, categoryRes, recentRes] = await Promise.all([
            fetch(`${FEEDBACK_API_BASE}/stats`),
            fetch(`${FEEDBACK_API_BASE}/sentiment/all?limit=100`),
            fetch(`${FEEDBACK_API_BASE}/sentiment/trend?days=${days}`),
            fetch(`${FEEDBACK_API_BASE}/sentiment/by-category`),
            fetch(`${FEEDBACK_API_BASE}/recent?limit=20`)
        ]);

        const statsData = await statsRes.json();
        const sentimentData = await sentimentRes.json();
        const trendData = await trendRes.json();
        const categoryData = await categoryRes.json();
        const recentData = await recentRes.json();

        // Update stats cards
        if (statsData.status === 'success') {
            updateStatsCards(statsData.stats, sentimentData.summary);
        }

        // Update charts
        if (sentimentData.status === 'success') {
            updateSentimentChart(sentimentData.summary);
            updateNLPSummary(sentimentData.summary);
        }

        if (statsData.status === 'success') {
            updateRatingChart(statsData.stats.rating_distribution);
        }

        if (trendData.status === 'success') {
            updateSentimentTrendChart(trendData.trend);
        }

        if (categoryData.status === 'success') {
            updateCategorySentimentChart(categoryData.categories);
        }

        // Update feedback table
        if (recentData.status === 'success') {
            updateFeedbackTable(recentData.data);
        }

    } catch (error) {
        console.error('Error loading feedback data:', error);
    }
}

// Update stats cards
function updateStatsCards(stats, sentimentSummary) {
    const totalFeedback = document.getElementById('totalFeedback');
    const avgRating = document.getElementById('avgRating');
    const positivePercent = document.getElementById('positivePercent');
    const negativePercent = document.getElementById('negativePercent');

    if (totalFeedback) totalFeedback.textContent = stats.total_feedback || 0;
    if (avgRating) avgRating.textContent = (stats.average_rating || 0).toFixed(1) + ' ★';

    if (sentimentSummary) {
        if (positivePercent) positivePercent.textContent = (sentimentSummary.positive_percentage || 0) + '%';
        if (negativePercent) negativePercent.textContent = (sentimentSummary.negative_percentage || 0) + '%';
    }
}

// Update NLP Summary
function updateNLPSummary(summary) {
    const container = document.getElementById('nlpSummary');
    if (!container || !summary) return;

    const getHealthStatus = (positivePercentage) => {
        if (positivePercentage >= 70) return { label: 'Sangat Baik', color: '#22c55e', emoji: '😊' };
        if (positivePercentage >= 50) return { label: 'Baik', color: '#84cc16', emoji: '🙂' };
        if (positivePercentage >= 30) return { label: 'Perlu Perhatian', color: '#f59e0b', emoji: '😐' };
        return { label: 'Perlu Perbaikan', color: '#ef4444', emoji: '😟' };
    };

    const health = getHealthStatus(summary.positive_percentage || 0);

    container.innerHTML = `
        <div class="nlp-health-indicator" style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 48px; margin-bottom: 8px;">${health.emoji}</div>
            <div style="font-size: 18px; font-weight: 600; color: ${health.color};">${health.label}</div>
            <div style="font-size: 12px; color: var(--gray);">Kesehatan Sentimen</div>
        </div>
        
        <div class="nlp-stats-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div class="nlp-stat-item" style="background: #e8f9d8; padding: 12px; border-radius: 8px; text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #2d6b2f;">${summary.sentiment_distribution?.positive || 0}</div>
                <div style="font-size: 11px; color: #3f7218;">Positif</div>
            </div>
            <div class="nlp-stat-item" style="background: #fee2e2; padding: 12px; border-radius: 8px; text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #991b1b;">${summary.sentiment_distribution?.negative || 0}</div>
                <div style="font-size: 11px; color: #dc2626;">Negatif</div>
            </div>
            <div class="nlp-stat-item" style="background: #e5e7eb; padding: 12px; border-radius: 8px; text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #4b5563;">${summary.sentiment_distribution?.neutral || 0}</div>
                <div style="font-size: 11px; color: #6b7280;">Netral</div>
            </div>
            <div class="nlp-stat-item" style="background: #dbeafe; padding: 12px; border-radius: 8px; text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #1e40af;">${(summary.average_confidence * 100 || 0).toFixed(0)}%</div>
                <div style="font-size: 11px; color: #3b82f6;">Akurasi</div>
            </div>
        </div>
        
        <div style="margin-top: 16px; padding: 12px; background: var(--bg); border-radius: 8px;">
            <div style="font-size: 12px; color: var(--gray); margin-bottom: 4px;">Total Dianalisis</div>
            <div style="font-size: 18px; font-weight: 600;">${summary.total_analyzed || 0} feedback</div>
        </div>
    `;
}

// Update Sentiment Distribution Chart (Doughnut)
function updateSentimentChart(summary) {
    const ctx = document.getElementById('sentimentChart');
    if (!ctx) return;

    const data = {
        labels: ['Positif', 'Negatif', 'Netral'],
        datasets: [{
            data: [
                summary.sentiment_distribution?.positive || 0,
                summary.sentiment_distribution?.negative || 0,
                summary.sentiment_distribution?.neutral || 0
            ],
            backgroundColor: [
                'rgba(34, 197, 94, 0.8)',
                'rgba(239, 68, 68, 0.8)',
                'rgba(156, 163, 175, 0.8)'
            ],
            borderColor: [
                'rgba(34, 197, 94, 1)',
                'rgba(239, 68, 68, 1)',
                'rgba(156, 163, 175, 1)'
            ],
            borderWidth: 2,
            hoverOffset: 10
        }]
    };

    if (sentimentChart) {
        sentimentChart.data = data;
        sentimentChart.update();
    } else {
        sentimentChart = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: { size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((context.raw / total) * 100).toFixed(1) : 0;
                                return `${context.label}: ${context.raw} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }
}

// Update Rating Distribution Chart (Bar)
function updateRatingChart(ratingDistribution) {
    const ctx = document.getElementById('ratingChart');
    if (!ctx) return;

    const labels = ['⭐ 1', '⭐ 2', '⭐ 3', '⭐ 4', '⭐ 5'];
    const values = [
        ratingDistribution['1'] || 0,
        ratingDistribution['2'] || 0,
        ratingDistribution['3'] || 0,
        ratingDistribution['4'] || 0,
        ratingDistribution['5'] || 0
    ];

    const data = {
        labels: labels,
        datasets: [{
            label: 'Jumlah Feedback',
            data: values,
            backgroundColor: [
                'rgba(239, 68, 68, 0.7)',
                'rgba(249, 115, 22, 0.7)',
                'rgba(234, 179, 8, 0.7)',
                'rgba(132, 204, 22, 0.7)',
                'rgba(34, 197, 94, 0.7)'
            ],
            borderColor: [
                'rgba(239, 68, 68, 1)',
                'rgba(249, 115, 22, 1)',
                'rgba(234, 179, 8, 1)',
                'rgba(132, 204, 22, 1)',
                'rgba(34, 197, 94, 1)'
            ],
            borderWidth: 2,
            borderRadius: 8
        }]
    };

    if (ratingChart) {
        ratingChart.data = data;
        ratingChart.update();
    } else {
        ratingChart = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 },
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
}

// Update Sentiment Trend Chart (Line)
function updateSentimentTrendChart(trendData) {
    const ctx = document.getElementById('sentimentTrendChart');
    if (!ctx) return;

    const labels = trendData.map(d => {
        const date = new Date(d.date);
        return date.toLocaleDateString('id-ID', { day: 'numeric', month: 'short' });
    });

    const data = {
        labels: labels,
        datasets: [
            {
                label: 'Positif',
                data: trendData.map(d => d.positive),
                borderColor: 'rgba(34, 197, 94, 1)',
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6
            },
            {
                label: 'Negatif',
                data: trendData.map(d => d.negative),
                borderColor: 'rgba(239, 68, 68, 1)',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6
            },
            {
                label: 'Netral',
                data: trendData.map(d => d.neutral),
                borderColor: 'rgba(156, 163, 175, 1)',
                backgroundColor: 'rgba(156, 163, 175, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6
            }
        ]
    };

    if (sentimentTrendChart) {
        sentimentTrendChart.data = data;
        sentimentTrendChart.update();
    } else {
        sentimentTrendChart = new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        stacked: false,
                        grid: { color: 'rgba(0,0,0,0.05)' },
                        ticks: { stepSize: 1 }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
}

// Update Category Sentiment Chart (Horizontal Bar)
function updateCategorySentimentChart(categories) {
    const ctx = document.getElementById('categorySentimentChart');
    if (!ctx) return;

    // Take top 6 categories
    const topCategories = categories.slice(0, 6);
    const labels = topCategories.map(c => c.category);

    const data = {
        labels: labels,
        datasets: [
            {
                label: 'Positif',
                data: topCategories.map(c => c.positive),
                backgroundColor: 'rgba(34, 197, 94, 0.8)',
                borderColor: 'rgba(34, 197, 94, 1)',
                borderWidth: 1
            },
            {
                label: 'Negatif',
                data: topCategories.map(c => c.negative),
                backgroundColor: 'rgba(239, 68, 68, 0.8)',
                borderColor: 'rgba(239, 68, 68, 1)',
                borderWidth: 1
            },
            {
                label: 'Netral',
                data: topCategories.map(c => c.neutral),
                backgroundColor: 'rgba(156, 163, 175, 0.8)',
                borderColor: 'rgba(156, 163, 175, 1)',
                borderWidth: 1
            }
        ]
    };

    if (categorySentimentChart) {
        categorySentimentChart.data = data;
        categorySentimentChart.update();
    } else {
        categorySentimentChart = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 10,
                            font: { size: 11 }
                        }
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    y: {
                        stacked: true,
                        grid: { display: false }
                    }
                }
            }
        });
    }
}

// Update Feedback Table
function updateFeedbackTable(feedbacks) {
    const tbody = document.getElementById('feedbackTableBody');
    if (!tbody) return;

    if (!feedbacks || feedbacks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="loading">Tidak ada data feedback</td></tr>';
        return;
    }

    tbody.innerHTML = feedbacks.map(fb => {
        const sentimentBadge = getSentimentBadge(fb.sentiment);
        const ratingStars = '★'.repeat(fb.rating) + '☆'.repeat(5 - fb.rating);

        return `
            <tr>
                <td>${fb.id}</td>
                <td>${fb.user_name || 'Unknown'}</td>
                <td><span class="badge badge-info">${fb.category || '-'}</span></td>
                <td><span style="color: #f59e0b;">${ratingStars}</span></td>
                <td class="text-truncate" title="${escapeHtml(fb.message)}">${truncateText(fb.message, 50)}</td>
                <td>${sentimentBadge}</td>
                <td>
                    <span class="badge ${fb.sentiment_score > 0 ? 'badge-success' : fb.sentiment_score < 0 ? 'badge-danger' : 'badge-info'}">
                        ${fb.sentiment_score > 0 ? '+' : ''}${fb.sentiment_score.toFixed(2)}
                    </span>
                </td>
                <td>${formatDate(fb.created_at)}</td>
            </tr>
        `;
    }).join('');
}

// Helper Functions
function getSentimentBadge(sentiment) {
    const badges = {
        'positive': '<span class="badge badge-success">😊 Positif</span>',
        'negative': '<span class="badge badge-danger">😟 Negatif</span>',
        'neutral': '<span class="badge" style="background: #e5e7eb; color: #4b5563;">😐 Netral</span>'
    };
    return badges[sentiment] || badges['neutral'];
}

function truncateText(text, maxLength) {
    if (!text) return '-';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });
}

// Extend the existing switchSection function to handle feedback
const originalSwitchSection = window.switchSection;
if (originalSwitchSection) {
    window.switchSection = function (section) {
        originalSwitchSection(section);
        if (section === 'feedback') {
            initFeedbackDashboard();
        }
    };
}

// Also add to loadSectionData for compatibility
const originalLoadSectionData = window.loadSectionData;
window.loadSectionData = function (section) {
    if (section === 'feedback') {
        initFeedbackDashboard();
    } else if (originalLoadSectionData) {
        originalLoadSectionData(section);
    }
};

// Add feedback to page titles
document.addEventListener('DOMContentLoaded', function () {
    // Extend titles object if needed
    setTimeout(() => {
        // Initial load if feedback section is active
        const feedbackSection = document.getElementById('feedback-section');
        if (feedbackSection && feedbackSection.classList.contains('active')) {
            initFeedbackDashboard();
        }
    }, 500);
});
