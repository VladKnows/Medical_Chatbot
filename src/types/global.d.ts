// Global type declarations for path aliases
declare module '@/lib/utils' {
  import { ClassValue } from 'clsx';
  export function cn(...inputs: ClassValue[]): string;
}

declare module '@/lib/*' {
  const content: any;
  export default content;
}

declare module '@/components/*' {
  const content: any;
  export default content;
}

declare module '@/pages/*' {
  const content: any;
  export default content;
}

declare module '@/hooks/*' {
  const content: any;
  export default content;
}

declare module '@/assets/*' {
  const content: any;
  export default content;
}