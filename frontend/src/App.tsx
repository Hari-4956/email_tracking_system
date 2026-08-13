import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './layouts/AppLayout'
import { AnalyticsPage } from './pages/Analytics'
import { CampaignDetailPage } from './pages/CampaignDetail'
import { CampaignsPage } from './pages/Campaigns'
import { DashboardPage } from './pages/Dashboard'
import { NotFoundPage } from './pages/NotFound'
import { RecipientDetailsPage } from './pages/RecipientDetails'
import { RecipientsPage } from './pages/Recipients'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="campaigns" element={<CampaignsPage />} />
          <Route path="campaigns/:campaignId" element={<CampaignDetailPage />} />
          <Route path="recipients" element={<RecipientsPage />} />
          <Route path="recipients/:recipientId" element={<RecipientDetailsPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="home" element={<Navigate to="/" replace />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
