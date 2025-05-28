import { Button } from '@/components/ui/button';
import { Link as RouterLink } from 'react-router-dom';

const Header = () => {
  return (
    <header className="bg-blue-600 text-white py-4">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">
          <RouterLink to="/">Document Analyser</RouterLink>
        </h1>
        <Button asChild variant="ghost" className="text-white hover:bg-blue-700">
          <RouterLink to="/">Home</RouterLink>
        </Button>
      </div>
    </header>
  );
};

export default Header;
