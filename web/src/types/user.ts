export type User = {
    email: string;
    username: string;
    id: number;
    total_points: number;
    current_streak: number;
    last_activity_date: string;
    created_at: string;
};

export type Badge = {
    id: number;
    name: string;
    description: string;
    icon: string;
    points_required: number;
    tasks_required: number;
};

export type UserBadge = {
    badge: Badge;
    earned_at: string;
};

export type UserDashboard = {
    user: User;
    tasks: any[];
    badges: UserBadge[];
};