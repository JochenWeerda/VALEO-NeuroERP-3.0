import React from 'react';
import { View, StyleSheet } from 'react-native';
import { IconButton, useTheme } from 'react-native-paper';
import { useDispatch } from 'react-redux';
import { logout } from '../../store/slices/authSlice';

export default function HeaderRight() {
  const theme = useTheme();
  const dispatch = useDispatch();

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <View style={styles.container}>
      <IconButton
        icon="logout"
        size={24}
        onPress={handleLogout}
        iconColor={theme.colors.onPrimary}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
  },
});