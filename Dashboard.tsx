import { Line, Bar, Pie } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

interface MetricCardProps {
  title: string
  value: string | number
  change?: number
  icon: React.ReactNode
}

function MetricCard({ title, value, change, icon }: MetricCardProps) {
  return (
    <div className="bg-white/5 rounded-xl p-6 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-200">{title}</h3>
        {icon}
      </div>
      <div className="flex items-end justify-between">
        <div>
          <p className="text-2xl font-semibold">{value}</p>
          {change !== undefined && (
            <p className={`text-sm ${change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {change >= 0 ? '+' : ''}{change}%
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  // Dados de exemplo
  const lineChartData = {
    labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    datasets: [
      {
        label: 'Impressões',
        data: [1200, 1900, 3000, 5000, 4000, 3000],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.4
      }
    ]
  }

  const barChartData = {
    labels: ['Google Ads', 'Facebook Ads'],
    datasets: [
      {
        label: 'Investimento',
        data: [12000, 8000],
        backgroundColor: ['rgba(54, 162, 235, 0.5)', 'rgba(75, 192, 192, 0.5)']
      }
    ]
  }

  const pieChartData = {
    labels: ['Campanha 1', 'Campanha 2', 'Campanha 3'],
    datasets: [
      {
        data: [300, 200, 100],
        backgroundColor: [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(75, 192, 192, 0.5)'
        ]
      }
    ]
  }

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <MetricCard
          title="Impressões"
          value="125.3k"
          change={12.5}
          icon={<span>👁️</span>}
        />
        <MetricCard
          title="Cliques"
          value="3.2k"
          change={-2.3}
          icon={<span>🖱️</span>}
        />
        <MetricCard
          title="CTR"
          value="2.56%"
          change={0.8}
          icon={<span>📊</span>}
        />
        <MetricCard
          title="CPC Médio"
          value="R$ 1.23"
          change={-5.2}
          icon={<span>💰</span>}
        />
        <MetricCard
          title="Conversões"
          value="156"
          change={15.7}
          icon={<span>🎯</span>}
        />
        <MetricCard
          title="ROAS"
          value="3.2x"
          change={8.4}
          icon={<span>📈</span>}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white/5 rounded-xl p-6">
          <h3 className="text-lg font-medium mb-4">Evolução de Impressões</h3>
          <Line data={lineChartData} options={{ responsive: true }} />
        </div>
        <div className="bg-white/5 rounded-xl p-6">
          <h3 className="text-lg font-medium mb-4">Investimento por Canal</h3>
          <Bar data={barChartData} options={{ responsive: true }} />
        </div>
      </div>

      <div className="bg-white/5 rounded-xl p-6">
        <h3 className="text-lg font-medium mb-4">Distribuição de Campanhas</h3>
        <div className="h-[300px]">
          <Pie data={pieChartData} options={{ responsive: true, maintainAspectRatio: false }} />
        </div>
      </div>
    </div>
  )
} 