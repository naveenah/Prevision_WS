import React from 'react';

interface BrandCardProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  className?: string;
  children?: React.ReactNode;
}

/**
 * @description Standardized glass-morphism card for the AI Brand Automator interface.
 * Copilot: Use this for all dashboard widgets and content containers.
 * 
 * @example
 * <BrandCard
 *   title="Brand Strategy"
 *   description="AI-powered brand vision and mission"
 *   icon={<SparklesIcon className="w-6 h-6" />}
 * />
 */
export const BrandCard = ({
  title,
  description,
  icon,
  className = '',
  children,
}: BrandCardProps) => {
  return (
    <div
      className={`glass-card p-6 group hover:border-brand-electric/50 transition-all duration-300 ${className}`}
    >
      <div className="flex items-center gap-4 mb-4">
        {icon && (
          <div className="text-brand-electric group-hover:scale-110 transition-transform duration-300">
            {icon}
          </div>
        )}
        <h3 className="text-xl font-heading text-white">{title}</h3>
      </div>
      <p className="text-brand-silver/70 leading-relaxed font-body">
        {description}
      </p>
      {children && <div className="mt-4">{children}</div>}
    </div>
  );
};

/**
 * @description Variant of BrandCard with AI pulse animation.
 * Use when displaying AI-processing states or automated content.
 */
export const BrandCardPulse = (props: BrandCardProps) => {
  return <BrandCard {...props} className={`ai-pulse ${props.className || ''}`} />;
};

export default BrandCard;
