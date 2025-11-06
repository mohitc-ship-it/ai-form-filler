import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ProcessButtonProps {
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
}

export const ProcessButton = ({ onClick, disabled, loading }: ProcessButtonProps) => {
  return (
    <div className="flex items-center justify-center">
      <Button
        onClick={onClick}
        disabled={disabled || loading}
        size="lg"
        className={cn(
          "gap-2 px-8 py-6 text-lg font-semibold shadow-lg hover:shadow-xl transition-all",
          "bg-gradient-to-r from-primary to-primary-glow hover:scale-105",
          loading && "animate-pulse"
        )}
      >
        <Sparkles className={cn("w-5 h-5", loading && "animate-spin")} />
        {loading ? "Processing..." : "Fill Documents with AI"}
      </Button>
    </div>
  );
};
