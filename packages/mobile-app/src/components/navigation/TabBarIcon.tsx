import React from 'react';
import { View } from 'react-native';
import { useTheme } from 'react-native-paper';
import * as Icons from '@expo/vector-icons';

interface TabBarIconProps {
  route: { name: string };
  focused: boolean;
  color: string;
  size: number;
}

export default function TabBarIcon({ route, focused, color, size }: TabBarIconProps) {
  const theme = useTheme();

  const getIconName = (routeName: string): keyof typeof Icons => {
    switch (routeName) {
      case 'Dashboard':
        return 'home';
      case 'Customers':
        return 'users';
      case 'Leads':
        return 'user-plus';
      case 'Tasks':
        return 'check-square';
      case 'Settings':
        return 'settings';
      default:
        return 'circle';
    }
  };

  const IconComponent = Icons.MaterialCommunityIcons;
  const iconName = getIconName(route.name);

  return (
    <View>
      <IconComponent
        name={iconName as any}
        size={size}
        color={focused ? theme.colors.primary : color}
      />
    </View>
  );
}