import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Switch } from "@/components/ui/switch";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  Briefcase,
  CheckCircle2,
  Clock,
  DollarSign,
  FileText,
  LayoutDashboard,
  Menu,
  MessageSquare,
  Plus,
  Search,
  Settings,
  Star,
  TrendingUp,
  User,
  X,
  Zap,
} from "lucide-react";
import { useState } from "react";

const stats = [
  { label: "Активных проектов", value: "12", icon: Briefcase },
  { label: "Завершено", value: "86", icon: CheckCircle2 },
  { label: "Доход за месяц", value: "₽284 000", icon: DollarSign },
  { label: "Рейтинг", value: "4.9", icon: Star },
];

const projects = [
  { name: "Редизайн интернет-магазина", client: "ООО «Прогресс»", status: "В работе", progress: 65 },
  { name: "Мобильное приложение", client: "Стартап «Волна»", status: "В работе", progress: 30 },
  { name: "Лендинг для конференции", client: "EventPro", status: "Ревью", progress: 90 },
  { name: "Корпоративный портал", client: "ТехноГрупп", status: "Завершён", progress: 100 },
];

const tasks = [
  { text: "Согласовать макеты главной страницы", done: true },
  { text: "Подготовить прототип мобильной версии", done: false },
  { text: "Отправить счёт за октябрь", done: false },
  { text: "Обновить портфолио", done: true },
  { text: "Созвон с клиентом в 15:00", done: false },
];

const messages = [
  { from: "Алексей К.", text: "Готовы утвердить финальный вариант?", time: "10 мин" },
  { from: "Мария С.", text: "Пришлите пожалуйста обновлённые макеты", time: "1 час" },
  { from: "EventPro", text: "Лендинг выглядит отлично, спасибо!", time: "3 часа" },
];

const navItems = [
  { icon: LayoutDashboard, label: "Обзор" },
  { icon: Briefcase, label: "Проекты" },
  { icon: MessageSquare, label: "Сообщения" },
  { icon: FileText, label: "Счета" },
  { icon: Settings, label: "Настройки" },
];

const StatusBadge = ({ status }: { status: string }) => {
  const isComplete = status === "Завершён";
  const isReview = status === "Ревью";
  return (
    <Badge
      variant={isComplete ? "default" : "outline"}
      className={
        isComplete
          ? "bg-primary text-primary-foreground"
          : isReview
          ? "border-primary text-foreground"
          : "border-foreground text-foreground"
      }
    >
      {status}
    </Badge>
  );
};

const Index = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchValue, setSearchValue] = useState("");

  return (
    <div className="min-h-screen bg-background text-foreground font-sans">
      {/* Header */}
      <header className="border-b border-foreground/10 sticky top-0 bg-background z-50">
        <div className="container-main flex items-center justify-between h-14">
          <div className="flex items-center gap-3">
            <Zap className="w-6 h-6 text-primary" strokeWidth={2.5} />
            <span className="text-lg font-semibold tracking-tight">Фрилансер</span>
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <button
                key={item.label}
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors duration-150 rounded hover:bg-muted"
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </button>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center relative">
              <Search className="w-4 h-4 absolute left-3 text-muted-foreground" />
              <Input
                placeholder="Поиск..."
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                className="pl-9 w-48 h-9 bg-muted border-none text-sm"
              />
            </div>
            <Button size="sm" className="hidden sm:inline-flex">
              <Plus className="w-4 h-4" />
              Новый проект
            </Button>
            <button
              className="md:hidden p-2 hover:bg-muted rounded transition-colors duration-150"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Меню"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <nav className="md:hidden border-t border-foreground/10 bg-background">
            <div className="container-main py-2 space-y-1">
              {navItems.map((item) => (
                <button
                  key={item.label}
                  className="flex items-center gap-3 w-full px-3 py-3 text-sm font-medium text-foreground hover:bg-muted rounded transition-colors duration-150"
                >
                  <item.icon className="w-5 h-5" />
                  {item.label}
                </button>
              ))}
              <Separator className="bg-foreground/10" />
              <div className="flex items-center relative py-1">
                <Search className="w-4 h-4 absolute left-3 text-muted-foreground" />
                <Input
                  placeholder="Поиск..."
                  className="pl-9 bg-muted border-none text-sm"
                />
              </div>
              <Button className="w-full">
                <Plus className="w-4 h-4" />
                Новый проект
              </Button>
            </div>
          </nav>
        )}
      </header>

      <main className="container-main py-8 space-y-10">
        {/* Hero Section */}
        <section>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">
            Добро пожаловать, Иван
          </h1>
          <p className="text-muted-foreground mt-2 text-base">
            Вот что происходит с вашими проектами сегодня.
          </p>
        </section>

        {/* Stats */}
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="border border-foreground/10 rounded p-5 flex flex-col gap-3 hover:border-primary transition-colors duration-150"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">{stat.label}</span>
                <stat.icon className="w-5 h-5 text-primary" />
              </div>
              <span className="text-2xl font-bold">{stat.value}</span>
            </div>
          ))}
        </section>

        {/* Projects + Tasks */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Projects List */}
          <section className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Проекты</h2>
              <Button variant="ghost" size="sm">
                Все проекты
                <TrendingUp className="w-4 h-4" />
              </Button>
            </div>
            <div className="border border-foreground/10 rounded divide-y divide-foreground/10">
              {projects.map((project) => (
                <div
                  key={project.name}
                  className="p-4 sm:p-5 hover:bg-muted/50 transition-colors duration-150 cursor-pointer"
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="min-w-0">
                      <h3 className="font-medium text-sm sm:text-base truncate">{project.name}</h3>
                      <p className="text-sm text-muted-foreground">{project.client}</p>
                    </div>
                    <StatusBadge status={project.status} />
                  </div>
                  <div className="flex items-center gap-3">
                    <Progress value={project.progress} className="h-1.5 flex-1 bg-muted [&>div]:bg-primary" />
                    <span className="text-xs text-muted-foreground font-medium w-8 text-right">
                      {project.progress}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Tasks */}
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Задачи</h2>
              <Button variant="ghost" size="icon" className="w-8 h-8">
                <Plus className="w-4 h-4" />
              </Button>
            </div>
            <div className="border border-foreground/10 rounded divide-y divide-foreground/10">
              {tasks.map((task, i) => (
                <label
                  key={i}
                  className="flex items-start gap-3 p-4 hover:bg-muted/50 transition-colors duration-150 cursor-pointer"
                >
                  <Checkbox
                    defaultChecked={task.done}
                    className="mt-0.5 border-foreground/30 data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                  />
                  <span
                    className={`text-sm leading-snug ${
                      task.done ? "line-through text-muted-foreground" : ""
                    }`}
                  >
                    {task.text}
                  </span>
                </label>
              ))}
            </div>
          </section>
        </div>

        {/* Messages + Elements Showcase */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Messages */}
          <section className="space-y-4">
            <h2 className="text-xl font-semibold">Сообщения</h2>
            <div className="border border-foreground/10 rounded divide-y divide-foreground/10">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className="p-4 flex items-start gap-3 hover:bg-muted/50 transition-colors duration-150 cursor-pointer"
                >
                  <div className="w-9 h-9 rounded-full bg-muted flex items-center justify-center shrink-0">
                    <User className="w-4 h-4 text-muted-foreground" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-sm">{msg.from}</span>
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {msg.time}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground truncate mt-0.5">{msg.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* UI Elements Showcase */}
          <section className="space-y-4">
            <h2 className="text-xl font-semibold">Элементы интерфейса</h2>
            <div className="border border-foreground/10 rounded p-5 space-y-6">
              {/* Buttons */}
              <div className="space-y-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Кнопки
                </span>
                <div className="flex flex-wrap gap-2">
                  <Button>Основная</Button>
                  <Button variant="secondary">Вторичная</Button>
                  <Button variant="outline">Контурная</Button>
                  <Button variant="ghost">Прозрачная</Button>
                  <Button variant="destructive">Удалить</Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button size="sm">Маленькая</Button>
                  <Button size="lg">Большая</Button>
                  <Button size="icon">
                    <Plus className="w-4 h-4" />
                  </Button>
                  <Button disabled>Неактивна</Button>
                </div>
              </div>

              <Separator className="bg-foreground/10" />

              {/* Badges */}
              <div className="space-y-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Бейджи
                </span>
                <div className="flex flex-wrap gap-2">
                  <Badge>По умолчанию</Badge>
                  <Badge variant="secondary">Вторичный</Badge>
                  <Badge variant="outline">Контурный</Badge>
                  <Badge variant="destructive">Ошибка</Badge>
                </div>
              </div>

              <Separator className="bg-foreground/10" />

              {/* Inputs */}
              <div className="space-y-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Поля ввода
                </span>
                <Input placeholder="Введите текст..." className="bg-muted border-foreground/10" />
                <Input
                  placeholder="Поиск по проектам..."
                  className="bg-muted border-foreground/10"
                  disabled
                />
              </div>

              <Separator className="bg-foreground/10" />

              {/* Toggle & Progress */}
              <div className="space-y-3">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Переключатели и прогресс
                </span>
                <div className="flex items-center gap-3">
                  <Switch />
                  <span className="text-sm">Уведомления по email</span>
                </div>
                <div className="flex items-center gap-3">
                  <Switch defaultChecked />
                  <span className="text-sm">Тёмная тема (скоро)</span>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>Загрузка файла</span>
                    <span className="text-muted-foreground">72%</span>
                  </div>
                  <Progress value={72} className="h-2 bg-muted [&>div]:bg-primary" />
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-foreground/10 mt-10">
        <div className="container-main py-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-primary" />
            <span>Фрилансер © 2026</span>
          </div>
          <div className="flex gap-4">
            <button className="hover:text-foreground transition-colors duration-150">Помощь</button>
            <button className="hover:text-foreground transition-colors duration-150">Условия</button>
            <button className="hover:text-foreground transition-colors duration-150">Контакты</button>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
